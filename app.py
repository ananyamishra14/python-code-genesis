
"""
Job-to-Be-Done Marketplace

This is the main application file for the Job-to-Be-Done Marketplace platform.
The platform allows users to submit problems (rather than job postings),
and AI decomposes these problems into tasks, sources solutions,
and manages micro-contractors.

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

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///marketplace.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure OpenAI API
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Configure Stripe API
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Define database models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    name = db.Column(db.String(100))
    is_contractor = db.Column(db.Boolean, default=False)
    skills = db.Column(db.String(500))
    stripe_customer_id = db.Column(db.String(100))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    budget = db.Column(db.Float)
    timeline = db.Column(db.Integer)  # In days
    status = db.Column(db.String(50), default='pending')  # pending, planning, in-progress, completed
    success_criteria = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_completed = db.Column(db.DateTime)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    contractor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    budget = db.Column(db.Float)
    timeline = db.Column(db.Integer)  # In days
    status = db.Column(db.String(50), default='open')  # open, assigned, in-progress, completed
    skills_required = db.Column(db.String(500))
    difficulty = db.Column(db.String(20))  # easy, medium, hard
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_completed = db.Column(db.DateTime)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    contractor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(50), default='pending')  # pending, accepted, rejected
    date_applied = db.Column(db.DateTime, default=datetime.utcnow)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    amount = db.Column(db.Float)
    status = db.Column(db.String(50))  # pending, completed, failed
    stripe_payment_id = db.Column(db.String(100))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# AI Task Decomposition
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
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that decomposes jobs into specific tasks."},
                {"role": "user", "content": prompt}
            ]
        )
        
        tasks = response.choices[0].message.content
        # In a real implementation, parse the JSON and validate
        return tasks
    except Exception as e:
        print(f"Error in AI decomposition: {e}")
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
        available_tasks = Task.query.filter_by(status='open').all()
        applications = Application.query.filter_by(contractor_id=current_user.id).all()
        applied_task_ids = [app.task_id for app in applications]
        applied_tasks = Task.query.filter(Task.id.in_(applied_task_ids)).all()
        
        return render_template('contractor_dashboard.html', 
                              available_tasks=available_tasks,
                              applied_tasks=applied_tasks)
    else:
        # For clients: show their jobs
        jobs = Job.query.filter_by(client_id=current_user.id).all()
        return render_template('client_dashboard.html', jobs=jobs)

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

# Main entry point
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
