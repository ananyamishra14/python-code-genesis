
"""
Smart Inventory & Demand Prediction System

This is the main application file for the Smart Inventory & Demand Prediction System.
The platform uses AI and machine learning to predict demand, optimize inventory levels,
and provide data-driven insights for retail inventory management.

Author: [Your Name]
"""

import os
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import openai
from datetime import datetime, timedelta
import stripe
import logging
from logging.handlers import RotatingFileHandler
import pandas as pd
import numpy as np
from endpoints import init_app as init_api_endpoints

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///inventory.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure logging
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Smart Inventory System startup')

# Initialize database
from models import db, User, Product, Category, Sale, InventoryChange, Prediction, ExternalFactor

db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure OpenAI API
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Configure Stripe API
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Initialize API endpoints
init_api_endpoints(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# AI Task Decomposition (retained from previous codebase)
def decompose_job(job_description, budget, timeline):
    """
    Use OpenAI to break down a job into smaller tasks
    """
    prompt = f"""
    As an AI project manager, break down the following job into 3-6 specific tasks:
    
    Job Description: {job_description}
    Total Budget: ${budget}
    Timeline: {timeline} days
    
    For each task, provide:
    1. Task title
    2. Detailed description
    3. Estimated budget (sum should not exceed total budget)
    4. Timeline in days (all tasks should fit within the total timeline)
    5. Required skills (comma separated)
    6. Difficulty level (easy, medium, or hard)
    
    Format the response as a JSON array of task objects.
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that decomposes jobs into specific tasks."},
                {"role": "user", "content": prompt}
            ]
        )
        
        tasks = response.choices[0].message.content
        # In a real implementation, parse the JSON and validate
        return tasks
    except Exception as e:
        app.logger.error(f"Error in AI decomposition: {e}")
        return None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        is_contractor = 'is_contractor' in request.form
        
        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        if user:
            return render_template('register.html', error='Email already registered')
        
        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = User(email=email, name=name, password=hashed_password, is_contractor=is_contractor)
        
        # Create Stripe customer
        customer = stripe.Customer.create(
            email=email,
            name=name
        )
        new_user.stripe_customer_id = customer.id
        
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password, password):
            return render_template('login.html', error='Invalid credentials')
        
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_contractor:
        # For contractors: show available tasks and applied tasks
        from models import Task, Application
        
        available_tasks = Task.query.filter_by(status='open').all()
        applications = Application.query.filter_by(contractor_id=current_user.id).all()
        applied_task_ids = [app.task_id for app in applications]
        applied_tasks = Task.query.filter(Task.id.in_(applied_task_ids)).all()
        
        return render_template('contractor_dashboard.html', 
                              available_tasks=available_tasks,
                              applied_tasks=applied_tasks)
    else:
        # For clients/retailers: show inventory dashboard
        low_stock_count = Product.query.filter(
            (Product.current_stock <= Product.reorder_point) & 
            (Product.is_active == True)
        ).count()
        
        total_products = Product.query.filter_by(is_active=True).count()
        
        # Get total inventory value
        products = Product.query.filter_by(is_active=True).all()
        total_value = sum(p.current_stock * p.price for p in products)
        
        # Get recent sales data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        recent_sales = Sale.query.filter(
            Sale.date >= start_date,
            Sale.date <= end_date
        ).all()
        
        total_sales = sum(sale.quantity for sale in recent_sales)
        total_revenue = sum(sale.total_price for sale in recent_sales)
        
        return render_template('inventory_dashboard.html',
                              low_stock_count=low_stock_count,
                              total_products=total_products,
                              total_value=total_value,
                              total_sales=total_sales,
                              total_revenue=total_revenue)

@app.route('/submit_problem', methods=['GET', 'POST'])
@login_required
def submit_problem():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        budget = float(request.form.get('budget'))
        timeline = int(request.form.get('timeline'))
        success_criteria = request.form.get('success_criteria')
        
        # Create new job
        from models import Job
        
        new_job = Job(
            title=title,
            description=description,
            client_id=current_user.id,
            budget=budget,
            timeline=timeline,
            success_criteria=success_criteria,
            status='planning'
        )
        
        db.session.add(new_job)
        db.session.commit()
        
        # AI decomposition
        tasks_json = decompose_job(description, budget, timeline)
        
        # In a real implementation, parse the JSON and create tasks
        # For this example, we'll create dummy tasks
        from models import Task
        
        task_budget = budget / 3
        task_timeline = timeline / 3
        
        skills = ["Content Writing", "SEO", "Web Development", "Marketing"]
        difficulties = ["easy", "medium", "hard"]
        
        for i in range(3):
            task = Task(
                job_id=new_job.id,
                title=f"Task {i+1} for {title}",
                description=f"This is an auto-generated task for {title}",
                budget=task_budget,
                timeline=task_timeline,
                skills_required=skills[i % len(skills)],
                difficulty=difficulties[i % len(difficulties)]
            )
            db.session.add(task)
        
        db.session.commit()
        
        return redirect(url_for('dashboard'))
    
    return render_template('submit_problem.html')

@app.route('/job/<int:job_id>')
@login_required
def view_job(job_id):
    from models import Job, Task
    
    job = Job.query.get_or_404(job_id)
    
    # Ensure user owns the job or is an admin
    if job.client_id != current_user.id:
        return redirect(url_for('dashboard'))
    
    tasks = Task.query.filter_by(job_id=job_id).all()
    return render_template('view_job.html', job=job, tasks=tasks)

@app.route('/apply_task/<int:task_id>', methods=['POST'])
@login_required
def apply_task(task_id):
    if not current_user.is_contractor:
        return jsonify({"error": "Only contractors can apply for tasks"}), 403
    
    # Check if already applied
    from models import Application
    
    existing_application = Application.query.filter_by(
        task_id=task_id, 
        contractor_id=current_user.id
    ).first()
    
    if existing_application:
        return jsonify({"error": "Already applied for this task"}), 400
    
    # Create new application
    application = Application(
        task_id=task_id,
        contractor_id=current_user.id
    )
    
    db.session.add(application)
    db.session.commit()
    
    return jsonify({"success": True})

@app.route('/create_payment', methods=['POST'])
@login_required
def create_payment():
    amount = request.json.get('amount')
    job_id = request.json.get('job_id')
    
    try:
        # Create payment intent with Stripe
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Amount in cents
            currency='usd',
            customer=current_user.stripe_customer_id,
            metadata={'job_id': job_id}
        )
        
        return jsonify({
            'clientSecret': intent.client_secret
        })
    except Exception as e:
        return jsonify(error=str(e)), 403

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('STRIPE_WEBHOOK_SECRET')
        )
    except ValueError as e:
        # Invalid payload
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return 'Invalid signature', 400

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Update payment status in database
        # In a real implementation, you would update your database here
        
    return 'Success', 200

# New Inventory Management Routes

@app.route('/inventory')
@login_required
def inventory_dashboard():
    # Redirect to React frontend for inventory management
    return render_template('inventory_dashboard.html')

@app.route('/inventory/products')
@login_required
def inventory_products():
    # Fetch products for server-side rendering
    products = Product.query.filter_by(is_active=True).all()
    categories = Category.query.all()
    
    return render_template('inventory_products.html', 
                          products=products, 
                          categories=categories)

@app.route('/inventory/product/<int:product_id>')
@login_required
def view_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Get sales history
    recent_sales = Sale.query.filter_by(product_id=product_id).order_by(Sale.date.desc()).limit(10).all()
    
    # Get inventory changes
    inventory_changes = InventoryChange.query.filter_by(product_id=product_id).order_by(InventoryChange.date.desc()).limit(10).all()
    
    # Get predictions if available
    predictions = Prediction.query.filter_by(product_id=product_id).order_by(Prediction.date).all()
    
    return render_template('view_product.html',
                          product=product,
                          recent_sales=recent_sales,
                          inventory_changes=inventory_changes,
                          predictions=predictions)

@app.route('/inventory/analytics')
@login_required
def inventory_analytics():
    # Redirect to React frontend for analytics
    return render_template('inventory_analytics.html')

@app.route('/inventory/predictions')
@login_required
def inventory_predictions():
    # Redirect to React frontend for predictions
    return render_template('inventory_predictions.html')

@app.route('/inventory/optimizer')
@login_required
def inventory_optimizer():
    # Redirect to React frontend for optimizer
    return render_template('inventory_optimizer.html')

# API route for generating predictions
@app.route('/api/generate-predictions/<int:product_id>', methods=['POST'])
@login_required
def generate_predictions(product_id):
    try:
        # Check if product exists
        product = Product.query.get_or_404(product_id)
        
        # Get historical sales data
        from prediction_utils import (DemandPredictor, get_sales_data, 
                                    get_external_factors)
        
        # Get past sales data for training
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)  # 6 months of data
        
        sales_data = get_sales_data(db, product_id, start_date, end_date)
        
        if sales_data.empty:
            return jsonify({'error': 'Insufficient sales data for predictions'}), 400
        
        # Get external factors
        external_factors = get_external_factors(db, start_date, end_date)
        
        # Get model type from request
        data = request.json
        model_type = data.get('model_type', 'prophet')  # Default to prophet
        
        # Initialize predictor
        predictor = DemandPredictor(model_type=model_type)
        
        # Preprocess data
        processed_data = predictor.preprocess_data(sales_data, external_factors)
        
        # Train model
        metrics = predictor.train(processed_data, product_id)
        
        # Generate predictions
        future_external_factors = None  # For a real implementation, you would predict these
        predictions = predictor.predict(horizon=30, external_factors=future_external_factors)
        
        # Clear old predictions
        old_predictions = Prediction.query.filter_by(product_id=product_id).all()
        for pred in old_predictions:
            db.session.delete(pred)
        
        # Store new predictions
        for _, row in predictions.iterrows():
            prediction = Prediction(
                product_id=product_id,
                date=row['date'],
                predicted_demand=row['predicted_demand'],
                confidence_lower=row['confidence_lower'],
                confidence_upper=row['confidence_upper'],
                factors=json.dumps({
                    'data_points': len(processed_data),
                    'features': predictor.features,
                    'metrics': metrics
                }),
                model_version=f"{model_type}-1.0"
            )
            db.session.add(prediction)
        
        db.session.commit()
        
        # Create response data
        result = {
            'product': {
                'id': product.id,
                'name': product.name,
                'sku': product.sku
            },
            'metrics': metrics,
            'predictions': [
                {
                    'date': row['date'].strftime('%Y-%m-%d') if isinstance(row['date'], datetime) else row['date'],
                    'predicted_demand': float(row['predicted_demand']),
                    'confidence_lower': float(row['confidence_lower']),
                    'confidence_upper': float(row['confidence_upper'])
                }
                for _, row in predictions.iterrows()
            ]
        }
        
        return jsonify(result)
    
    except Exception as e:
        app.logger.error(f"Error generating predictions: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Main entry point
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
