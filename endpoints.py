
"""
API Endpoints for Smart Inventory & Demand Prediction System.

This file contains the Flask routes that expose the API endpoints for the 
inventory management and demand prediction system.
"""

from flask import Blueprint, request, jsonify, current_app
import pandas as pd
import json
from datetime import datetime, timedelta
import sqlalchemy as sa
from models import (db, Product, Category, Sale, InventoryChange, 
                   Prediction, ExternalFactor, User)
from prediction_utils import (DemandPredictor, InventoryOptimizer, 
                             get_sales_data, get_external_factors,
                             generate_inventory_report)

# Create Blueprint for inventory API endpoints
inventory_api = Blueprint('inventory_api', __name__)

@inventory_api.route('/products', methods=['GET'])
def get_products():
    """Get all products."""
    try:
        query = sa.select(Product)
        
        # Filter by category if provided
        category_id = request.args.get('category_id')
        if category_id:
            query = query.where(Product.category_id == int(category_id))
        
        # Filter by active status
        is_active = request.args.get('is_active')
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            query = query.where(Product.is_active == is_active_bool)
        
        # Add ordering
        sort_by = request.args.get('sort_by', 'id')
        order = request.args.get('order', 'asc')
        
        if hasattr(Product, sort_by):
            sort_attr = getattr(Product, sort_by)
            query = query.order_by(sort_attr.desc() if order == 'desc' else sort_attr)
        
        # Execute query
        products = db.session.execute(query).scalars().all()
        
        # Format response
        result = []
        for product in products:
            # Get category name
            category_name = None
            if product.category_id:
                category_query = sa.select(Category.name).where(Category.id == product.category_id)
                category_name = db.session.execute(category_query).scalar()
            
            result.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'sku': product.sku,
                'category_id': product.category_id,
                'category_name': category_name,
                'price': product.price,
                'cost': product.cost,
                'current_stock': product.current_stock,
                'reorder_point': product.reorder_point,
                'optimal_stock': product.optimal_stock,
                'lead_time': product.lead_time,
                'is_active': product.is_active,
                'date_created': product.date_created.isoformat() if product.date_created else None,
                'stock_status': product.stock_status()
            })
        
        return jsonify(result)
    
    except Exception as e:
        current_app.logger.error(f"Error in get_products: {str(e)}")
        return jsonify({'error': str(e)}), 500

@inventory_api.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a single product by ID."""
    try:
        product = db.session.get(Product, product_id)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Get category name
        category_name = None
        if product.category_id:
            category_query = sa.select(Category.name).where(Category.id == product.category_id)
            category_name = db.session.execute(category_query).scalar()
        
        # Format response
        result = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'sku': product.sku,
            'category_id': product.category_id,
            'category_name': category_name,
            'price': product.price,
            'cost': product.cost,
            'current_stock': product.current_stock,
            'reorder_point': product.reorder_point,
            'optimal_stock': product.optimal_stock,
            'lead_time': product.lead_time,
            'is_active': product.is_active,
            'date_created': product.date_created.isoformat() if product.date_created else None,
            'stock_status': product.stock_status()
        }
        
        return jsonify(result)
    
    except Exception as e:
        current_app.logger.error(f"Error in get_product: {str(e)}")
        return jsonify({'error': str(e)}), 500

@inventory_api.route('/categories', methods=['GET'])
def get_categories():
    """Get all product categories."""
    try:
        query = sa.select(Category)
        
        # Filter by parent_id if provided
        parent_id = request.args.get('parent_id')
        if parent_id:
            if parent_id == 'null':
                query = query.where(Category.parent_id.is_(None))
            else:
                query = query.where(Category.parent_id == int(parent_id))
        
        # Execute query
        categories = db.session.execute(query).scalars().all()
        
        # Format response
        result = []
        for category in categories:
            result.append({
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'parent_id': category.parent_id
            })
        
        return jsonify(result)
    
    except Exception as e:
        current_app.logger.error(f"Error in get_categories: {str(e)}")
        return jsonify({'error': str(e)}), 500

@inventory_api.route('/sales/summary', methods=['GET'])
def get_sales_summary():
    """Get sales summary data with optional filters."""
    try:
        # Parse date range filters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date:
            # Default to last 30 days
            end_date_dt = datetime.now()
            start_date_dt = end_date_dt - timedelta(days=30)
            start_date = start_date_dt.strftime('%Y-%m-%d')
            end_date = end_date_dt.strftime('%Y-%m-%d')
        
        if start_date:
            start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
            if not end_date:
                end_date_dt = datetime.now()
            else:
                end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Base query
        query = sa.select(
            sa.func.count().label('total_orders'),
            sa.func.sum(Sale.quantity).label('total_quantity'),
            sa.func.sum(Sale.total_price).label('total_revenue'),
            sa.func.avg(Sale.unit_price).label('avg_unit_price')
        ).where(
            Sale.date >= start_date_dt,
            Sale.date <= end_date_dt
        )
        
        # Add product filter if provided
        product_id = request.args.get('product_id')
        if product_id:
            query = query.where(Sale.product_id == int(product_id))
        
        # Execute query
        result = db.session.execute(query).one()
        
        # Build response
        summary = {
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'total_orders': result.total_orders,
            'total_quantity': result.total_quantity,
            'total_revenue': float(result.total_revenue) if result.total_revenue else 0,
            'avg_unit_price': float(result.avg_unit_price) if result.avg_unit_price else 0
        }
        
        # Get comparison with previous period
        previous_start_dt = start_date_dt - (end_date_dt - start_date_dt)
        previous_end_dt = start_date_dt - timedelta(days=1)
        
        previous_query = sa.select(
            sa.func.sum(Sale.total_price).label('prev_revenue'),
            sa.func.sum(Sale.quantity).label('prev_quantity')
        ).where(
            Sale.date >= previous_start_dt,
            Sale.date <= previous_end_dt
        )
        
        if product_id:
            previous_query = previous_query.where(Sale.product_id == int(product_id))
        
        previous_result = db.session.execute(previous_query).one()
        
        # Calculate growth percentages
        prev_revenue = float(previous_result.prev_revenue) if previous_result.prev_revenue else 0
        prev_quantity = int(previous_result.prev_quantity) if previous_result.prev_quantity else 0
        
        if prev_revenue > 0:
            revenue_growth = ((summary['total_revenue'] - prev_revenue) / prev_revenue) * 100
        else:
            revenue_growth = None
        
        if prev_quantity > 0:
            quantity_growth = ((summary['total_quantity'] - prev_quantity) / prev_quantity) * 100
        else:
            quantity_growth = None
        
        summary['comparison'] = {
            'previous_period': {
                'start_date': previous_start_dt.strftime('%Y-%m-%d'),
                'end_date': previous_end_dt.strftime('%Y-%m-%d')
            },
            'revenue_growth': revenue_growth,
            'quantity_growth': quantity_growth,
            'previous_revenue': prev_revenue,
            'previous_quantity': prev_quantity
        }
        
        return jsonify(summary)
    
    except Exception as e:
        current_app.logger.error(f"Error in get_sales_summary: {str(e)}")
        return jsonify({'error': str(e)}), 500

@inventory_api.route('/sales/by-day', methods=['GET'])
def get_sales_by_day():
    """Get daily sales data for charting."""
    try:
        # Parse date range filters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date:
            # Default to last 30 days
            end_date_dt = datetime.now()
            start_date_dt = end_date_dt - timedelta(days=30)
            start_date = start_date_dt.strftime('%Y-%m-%d')
            end_date = end_date_dt.strftime('%Y-%m-%d')
        
        if start_date:
            start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
            if not end_date:
                end_date_dt = datetime.now()
            else:
                end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Base query
        query = sa.select(
            sa.func.date(Sale.date).label('date'),
            sa.func.sum(Sale.quantity).label('quantity'),
            sa.func.sum(Sale.total_price).label('revenue')
        ).where(
            Sale.date >= start_date_dt,
            Sale.date <= end_date_dt
        ).group_by(
            sa.func.date(Sale.date)
        ).order_by(
            sa.func.date(Sale.date)
        )
        
        # Add product filter if provided
        product_id = request.args.get('product_id')
        if product_id:
            query = query.where(Sale.product_id == int(product_id))
        
        # Execute query
        sales_by_day = db.session.execute(query).all()
        
        # Format result
        result = [
            {
                'date': row.date.strftime('%Y-%m-%d'),
                'quantity': row.quantity,
                'revenue': float(row.revenue)
            }
            for row in sales_by_day
        ]
        
        return jsonify(result)
    
    except Exception as e:
        current_app.logger.error(f"Error in get_sales_by_day: {str(e)}")
        return jsonify({'error': str(e)}), 500

@inventory_api.route('/sales/by-category', methods=['GET'])
def get_sales_by_category():
    """Get sales data grouped by product category."""
    try:
        # Parse date range filters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
            if not end_date:
                end_date_dt = datetime.now()
            else:
                end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            # Default to last 30 days
            end_date_dt = datetime.now()
            start_date_dt = end_date_dt - timedelta(days=30)
        
        # Build query
        query = sa.select(
            Category.name.label('category'),
            sa.func.sum(Sale.quantity).label('quantity'),
            sa.func.sum(Sale.total_price).label('revenue')
        ).select_from(
            Sale
        ).join(
            Product, Sale.product_id == Product.id
        ).join(
            Category, Product.category_id == Category.id
        ).where(
            Sale.date >= start_date_dt,
            Sale.date <= end_date_dt
        ).group_by(
            Category.name
        ).order_by(
            sa.desc('revenue')
        )
        
        # Execute query
        sales_by_category = db.session.execute(query).all()
        
        # Format result
        result = [
            {
                'category': row.category,
                'quantity': row.quantity,
                'revenue': float(row.revenue)
            }
            for row in sales_by_category
        ]
        
        return jsonify(result)
    
    except Exception as e:
        current_app.logger.error(f"Error in get_sales_by_category: {str(e)}")
        return jsonify({'error': str(e)}), 500

@inventory_api.route('/sales/top-products', methods=['GET'])
def get_top_products():
    """Get top selling products by quantity or revenue."""
    try:
        # Parse parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        metric = request.args.get('metric', 'revenue')  # 'revenue' or 'quantity'
        limit = int(request.args.get('limit', 10))
        
        if start_date:
            start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
            if not end_date:
                end_date_dt = datetime.now()
            else:
                end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            # Default to last 30 days
            end_date_dt = datetime.now()
            start_date_dt = end_date_dt - timedelta(days=30)
        
        # Build query
        order_by_col = sa.func.sum(Sale.total_price).label('revenue')
        if metric == 'quantity':
            order_by_col = sa.func.sum(Sale.quantity).label('quantity')
        
        query = sa.select(
            Product.id.label('product_id'),
            Product.name.label('product_name'),
            Product.sku.label('sku'),
            Category.name.label('category'),
            sa.func.sum(Sale.quantity).label('quantity'),
            sa.func.sum(Sale.total_price).label('revenue'),
            (sa.func.sum(Sale.total_price) / sa.func.sum(Sale.quantity)).label('avg_price')
        ).select_from(
            Sale
        ).join(
            Product, Sale.product_id == Product.id
        ).outerjoin(
            Category, Product.category_id == Category.id
        ).where(
            Sale.date >= start_date_dt,
            Sale.date <= end_date_dt
        ).group_by(
            Product.id, Product.name, Product.sku, Category.name
        ).order_by(
            sa.desc(metric)
        ).limit(limit)
        
        # Execute query
        top_products = db.session.execute(query).all()
        
        # Format result
        result = []
        for row in top_products:
            # Calculate profit and margin (simplified)
            product = db.session.get(Product, row.product_id)
            cost_per_unit = product.cost if product else 0
            total_cost = cost_per_unit * row.quantity
            profit = row.revenue - total_cost
            margin = profit / row.revenue if row.revenue > 0 else 0
            
            result.append({
                'id': row.product_id,
                'name': row.product_name,
                'sku': row.sku,
                'category': row.category or 'Uncategorized',
                'quantity': row.quantity,
                'revenue': float(row.revenue),
                'avg_price': float(row.avg_price) if row.avg_price else 0,
                'profit': profit,
                'margin': margin
            })
        
        return jsonify(result)
    
    except Exception as e:
        current_app.logger.error(f"Error in get_top_products: {str(e)}")
        return jsonify({'error': str(e)}), 500

@inventory_api.route('/inventory/status', methods=['GET'])
def get_inventory_status():
    """Get inventory status summary and alerts."""
    try:
        # Get all active products
        query = sa.select(Product).where(Product.is_active == True)
        products = db.session.execute(query).scalars().all()
        
        # Track inventory statistics
        total_products = len(products)
        total_items = sum(p.current_stock for p in products)
        total_value = sum(p.current_stock * p.price for p in products)
        total_cost = sum(p.current_stock * p.cost for p in products)
        
        # Count products by status
        status_counts = {
            'out_of_stock': 0,
            'low_stock': 0,
            'adequate': 0,
            'overstocked': 0
        }
        
        inventory_alerts = []
        
        for product in products:
            status = product.stock_status()
            status_counts[status] += 1
            
            # Generate alerts for problematic statuses
            if status in ['out_of_stock', 'low_stock']:
                inventory_alerts.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'sku': product.sku,
                    'current_stock': product.current_stock,
                    'reorder_point': product.reorder_point,
                    'alert_type': status,
                    'message': (
                        f"Out of stock - Reorder immediately" 
                        if status == 'out_of_stock' else
                        f"Low stock - Below reorder point ({product.current_stock} < {product.reorder_point})"
                    ),
                    'severity': 'critical' if status == 'out_of_stock' else 'warning'
                })
            elif status == 'overstocked' and product.optimal_stock and product.current_stock > product.optimal_stock * 1.5:
                inventory_alerts.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'sku': product.sku,
                    'current_stock': product.current_stock,
                    'optimal_stock': product.optimal_stock,
                    'alert_type': 'overstocked',
                    'message': f"Overstocked - Consider promotions ({product.current_stock} > {product.optimal_stock})",
                    'severity': 'info'
                })
        
        # Get category breakdown
        category_query = sa.select(
            Category.name.label('category'),
            sa.func.sum(Product.current_stock).label('items'),
            sa.func.sum(Product.current_stock * Product.price).label('value')
        ).select_from(
            Product
        ).join(
            Category, Product.category_id == Category.id
        ).where(
            Product.is_active == True
        ).group_by(
            Category.name
        ).order_by(
            sa.desc('value')
        )
        
        category_breakdown = db.session.execute(category_query).all()
        
        # Format result
        result = {
            'summary': {
                'total_products': total_products,
                'total_items': total_items,
                'total_value': total_value,
                'total_cost': total_cost,
                'status_counts': status_counts
            },
            'alerts': inventory_alerts,
            'category_breakdown': [
                {
                    'category': row.category,
                    'items': row.items,
                    'value': float(row.value)
                }
                for row in category_breakdown
            ]
        }
        
        return jsonify(result)
    
    except Exception as e:
        current_app.logger.error(f"Error in get_inventory_status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@inventory_api.route('/predictions/<int:product_id>', methods=['GET'])
def get_predictions(product_id):
    """Get demand predictions for a specific product."""
    try:
        # Check if product exists
        product = db.session.get(Product, product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Get existing predictions if available
        query = sa.select(Prediction).where(
            Prediction.product_id == product_id
        ).order_by(
            Prediction.date
        )
        
        existing_predictions = db.session.execute(query).scalars().all()
        
        if existing_predictions:
            # Return existing predictions
            result = [
                {
                    'date': prediction.date.strftime('%Y-%m-%d'),
                    'predicted_demand': float(prediction.predicted_demand),
                    'confidence_lower': float(prediction.confidence_lower) if prediction.confidence_lower else None,
                    'confidence_upper': float(prediction.confidence_upper) if prediction.confidence_upper else None,
                    'factors': json.loads(prediction.factors) if prediction.factors else None,
                    'model_version': prediction.model_version
                }
                for prediction in existing_predictions
            ]
            return jsonify(result)
        else:
            # Generate new predictions using the prediction utility
            # Get past sales data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=180)  # 6 months of data
            
            sales_data = get_sales_data(db, product_id, start_date, end_date)
            
            if sales_data.empty:
                return jsonify({'error': 'Insufficient sales data for predictions'}), 400
            
            # Get external factors
            external_factors = get_external_factors(db, start_date, end_date)
            
            # Initialize predictor
            predictor = DemandPredictor(model_type="prophet")
            
            # Preprocess data
            processed_data = predictor.preprocess_data(sales_data, external_factors)
            
            # Train model
            predictor.train(processed_data, product_id)
            
            # Generate predictions
            future_external_factors = None  # For a real implementation, you would predict these
            predictions = predictor.predict(horizon=30, external_factors=future_external_factors)
            
            # Store predictions in the database
            for _, row in predictions.iterrows():
                prediction = Prediction(
                    product_id=product_id,
                    date=row['date'],
                    predicted_demand=row['predicted_demand'],
                    confidence_lower=row['confidence_lower'],
                    confidence_upper=row['confidence_upper'],
                    factors=json.dumps({
                        'data_points': len(processed_data),
                        'features': predictor.features
                    }),
                    model_version="prophet-1.0"
                )
                db.session.add(prediction)
            
            db.session.commit()
            
            # Format result
            result = [
                {
                    'date': row['date'].strftime('%Y-%m-%d') if isinstance(row['date'], datetime) else row['date'],
                    'predicted_demand': float(row['predicted_demand']),
                    'confidence_lower': float(row['confidence_lower']),
                    'confidence_upper': float(row['confidence_upper'])
                }
                for _, row in predictions.iterrows()
            ]
            
            return jsonify(result)
    
    except Exception as e:
        current_app.logger.error(f"Error in get_predictions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@inventory_api.route('/optimize/inventory/<int:product_id>', methods=['POST'])
def optimize_inventory(product_id):
    """Optimize inventory levels for a specific product."""
    try:
        # Check if product exists
        product = db.session.get(Product, product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Get parameters from request
        data = request.json
        service_level = data.get('service_level', 0.95)  # Default to 95%
        lead_time = data.get('lead_time', product.lead_time)
        
        # Get predictions for the product
        predictions_query = sa.select(Prediction).where(
            Prediction.product_id == product_id
        ).order_by(
            Prediction.date
        ).limit(30)  # Use next 30 days of predictions
        
        predictions = db.session.execute(predictions_query).scalars().all()
        
        if not predictions:
            # We need to generate predictions first
            return jsonify({'error': 'No predictions available for this product'}), 400
        
        # Convert predictions to dataframe
        predictions_df = pd.DataFrame([
            {
                'date': pred.date,
                'predicted_demand': pred.predicted_demand,
                'confidence_lower': pred.confidence_lower,
                'confidence_upper': pred.confidence_upper
            }
            for pred in predictions
        ])
        
        # Initialize optimizer
        optimizer = InventoryOptimizer()
        
        # Calculate optimal stock levels
        optimal_levels = optimizer.calculate_optimal_stock(
            product, predictions_df, lead_time, service_level
        )
        
        # Calculate potential cost savings
        cost_analysis = optimizer.calculate_stock_costs(
            product, optimal_levels, days=30
        )
        
        # Update product with new optimal values
        product.reorder_point = optimal_levels['reorder_point']
        product.optimal_stock = optimal_levels['optimal_stock']
        product.last_updated = datetime.utcnow()
        
        db.session.commit()
        
        # Combine optimization results
        result = {**optimal_levels, 'cost_analysis': cost_analysis}
        
        return jsonify(result)
    
    except Exception as e:
        current_app.logger.error(f"Error in optimize_inventory: {str(e)}")
        return jsonify({'error': str(e)}), 500

@inventory_api.route('/reports/inventory', methods=['GET'])
def get_inventory_report():
    """Generate a comprehensive inventory report."""
    try:
        # Get parameters
        product_id = request.args.get('product_id')
        category_id = request.args.get('category_id')
        
        # Convert to integers if provided
        if product_id:
            product_id = int(product_id)
        if category_id:
            category_id = int(category_id)
        
        # Generate report
        report = generate_inventory_report(db, product_id, category_id)
        
        return jsonify(report)
    
    except Exception as e:
        current_app.logger.error(f"Error in get_inventory_report: {str(e)}")
        return jsonify({'error': str(e)}), 500

@inventory_api.route('/external-factors', methods=['GET'])
def get_external_factors_api():
    """Get external factors that may affect demand."""
    try:
        # Parse date range
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            start_date = (datetime.now() - timedelta(days=30)).date()
        
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end_date = (datetime.now() + timedelta(days=30)).date()
        
        # Query external factors
        query = sa.select(ExternalFactor).where(
            ExternalFactor.date >= start_date,
            ExternalFactor.date <= end_date
        ).order_by(
            ExternalFactor.date
        )
        
        factors = db.session.execute(query).scalars().all()
        
        # Format result
        result = [
            {
                'id': factor.id,
                'name': factor.name,
                'description': factor.description,
                'date': factor.date.strftime('%Y-%m-%d'),
                'impact_level': float(factor.impact_level) if factor.impact_level is not None else None,
                'category': factor.category,
                'data': json.loads(factor.data) if factor.data else None
            }
            for factor in factors
        ]
        
        return jsonify(result)
    
    except Exception as e:
        current_app.logger.error(f"Error in get_external_factors_api: {str(e)}")
        return jsonify({'error': str(e)}), 500

def init_app(app):
    """Register the blueprint with the Flask app."""
    app.register_blueprint(inventory_api, url_prefix='/api/inventory')
