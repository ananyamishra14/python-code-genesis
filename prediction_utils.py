
"""
Prediction utilities for the Smart Inventory & Demand Prediction System.

This file contains functions and classes for demand prediction,
inventory optimization, and related analytics.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from prophet import Prophet
import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DemandPredictor:
    """
    Class for predicting product demand based on historical data.
    """
    
    def __init__(self, model_type="prophet"):
        """
        Initialize the demand predictor.
        
        Args:
            model_type (str): Type of model to use ('prophet', 'randomforest', or 'neural')
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.features = []
    
    def preprocess_data(self, sales_data, external_factors=None):
        """
        Preprocess sales data for model training.
        
        Args:
            sales_data (pd.DataFrame): Historical sales data
            external_factors (pd.DataFrame, optional): External factors data
            
        Returns:
            pd.DataFrame: Processed data ready for training
        """
        # Ensure data is sorted by date
        sales_data = sales_data.sort_values('date')
        
        # Aggregate data by day if not already
        if 'quantity' in sales_data.columns:
            daily_data = sales_data.groupby(pd.Grouper(key='date', freq='D')).agg({
                'quantity': 'sum'
            }).reset_index()
        else:
            daily_data = sales_data
        
        # Fill missing dates
        date_range = pd.date_range(start=daily_data['date'].min(), 
                                  end=daily_data['date'].max(), 
                                  freq='D')
        full_date_df = pd.DataFrame({'date': date_range})
        daily_data = pd.merge(full_date_df, daily_data, on='date', how='left').fillna(0)
        
        # Add time-based features
        daily_data['dayofweek'] = daily_data['date'].dt.dayofweek
        daily_data['month'] = daily_data['date'].dt.month
        daily_data['year'] = daily_data['date'].dt.year
        daily_data['is_weekend'] = daily_data['dayofweek'].apply(lambda x: 1 if x >= 5 else 0)
        
        # Add lag features
        for lag in [1, 7, 14, 28]:
            daily_data[f'lag_{lag}'] = daily_data['quantity'].shift(lag).fillna(0)
        
        # Add rolling window features
        for window in [7, 14, 30]:
            daily_data[f'rolling_mean_{window}'] = daily_data['quantity'].rolling(window).mean().fillna(0)
            daily_data[f'rolling_std_{window}'] = daily_data['quantity'].rolling(window).std().fillna(0)
        
        # Merge external factors if provided
        if external_factors is not None:
            daily_data = pd.merge(daily_data, external_factors, on='date', how='left')
            # Fill missing external factor values
            for col in external_factors.columns:
                if col != 'date':
                    daily_data[col] = daily_data[col].fillna(0)
        
        # For Prophet, we need to rename columns
        if self.model_type == 'prophet':
            prophet_data = daily_data.rename(columns={'date': 'ds', 'quantity': 'y'})
            return prophet_data
        
        return daily_data
    
    def train(self, processed_data, product_id=None, test_size=0.2):
        """
        Train the prediction model.
        
        Args:
            processed_data (pd.DataFrame): Preprocessed data
            product_id (int, optional): Product ID for tracking
            test_size (float): Proportion of data to use for testing
            
        Returns:
            dict: Training metrics
        """
        if self.model_type == 'prophet':
            # Select only required columns for Prophet
            prophet_data = processed_data[['ds', 'y']]
            
            # Fit Prophet model
            self.model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                seasonality_mode='multiplicative'
            )
            
            # Add external regressors if available
            for col in processed_data.columns:
                if col not in ['ds', 'y', 'date', 'quantity']:
                    self.model.add_regressor(col)
                    self.features.append(col)
            
            self.model.fit(prophet_data)
            self.is_trained = True
            
            # Generate test predictions
            future = self.model.make_future_dataframe(periods=30)
            for feature in self.features:
                future[feature] = processed_data[feature].values[:len(future)]
            forecast = self.model.predict(future)
            
            # Calculate metrics on test set
            actual = processed_data['y'].values
            predicted = forecast['yhat'].values[:len(actual)]
            mse = np.mean((actual - predicted) ** 2)
            mae = np.mean(np.abs(actual - predicted))
            
            metrics = {
                'product_id': product_id,
                'model_type': 'prophet',
                'mse': mse,
                'mae': mae,
                'training_data_points': len(processed_data)
            }
            
        elif self.model_type == 'randomforest':
            # Drop date and prepare features
            if 'date' in processed_data.columns:
                features = processed_data.drop(['date', 'quantity'], axis=1)
            else:
                features = processed_data.drop(['ds', 'y'], axis=1)
            
            # Store feature names
            self.features = features.columns.tolist()
            
            # Get target
            if 'quantity' in processed_data.columns:
                target = processed_data['quantity']
            else:
                target = processed_data['y']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                features, target, test_size=test_size, shuffle=False
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train Random Forest model
            self.model = RandomForestRegressor(
                n_estimators=100, 
                max_depth=10,
                min_samples_split=5,
                random_state=42
            )
            self.model.fit(X_train_scaled, y_train)
            self.is_trained = True
            
            # Calculate metrics
            y_pred = self.model.predict(X_test_scaled)
            mse = np.mean((y_test - y_pred) ** 2)
            mae = np.mean(np.abs(y_test - y_pred))
            
            metrics = {
                'product_id': product_id,
                'model_type': 'randomforest',
                'mse': mse,
                'mae': mae,
                'training_data_points': len(X_train),
                'feature_importance': dict(zip(self.features, 
                                             self.model.feature_importances_))
            }
            
        elif self.model_type == 'neural':
            # Prepare features
            if 'date' in processed_data.columns:
                features = processed_data.drop(['date', 'quantity'], axis=1)
            else:
                features = processed_data.drop(['ds', 'y'], axis=1)
            
            # Store feature names
            self.features = features.columns.tolist()
            
            # Get target
            if 'quantity' in processed_data.columns:
                target = processed_data['quantity']
            else:
                target = processed_data['y']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                features, target, test_size=test_size, shuffle=False
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Build neural network
            model = tf.keras.Sequential([
                tf.keras.layers.Dense(64, activation='relu', input_shape=(X_train_scaled.shape[1],)),
                tf.keras.layers.Dropout(0.2),
                tf.keras.layers.Dense(32, activation='relu'),
                tf.keras.layers.Dropout(0.2),
                tf.keras.layers.Dense(1)
            ])
            
            model.compile(optimizer='adam', loss='mse', metrics=['mae'])
            
            # Train model
            early_stop = tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=5,
                restore_best_weights=True
            )
            
            history = model.fit(
                X_train_scaled, y_train,
                epochs=50,
                batch_size=32,
                validation_split=0.2,
                callbacks=[early_stop],
                verbose=0
            )
            
            self.model = model
            self.is_trained = True
            
            # Calculate metrics
            y_pred = model.predict(X_test_scaled)
            mse = np.mean((y_test - y_pred.flatten()) ** 2)
            mae = np.mean(np.abs(y_test - y_pred.flatten()))
            
            metrics = {
                'product_id': product_id,
                'model_type': 'neural',
                'mse': mse,
                'mae': mae,
                'training_data_points': len(X_train),
                'training_history': {
                    'loss': [float(x) for x in history.history['loss']],
                    'val_loss': [float(x) for x in history.history['val_loss']]
                }
            }
        
        logger.info(f"Model trained for product {product_id} with metrics: {metrics}")
        return metrics
    
    def predict(self, horizon=30, external_factors=None):
        """
        Generate predictions for the specified horizon.
        
        Args:
            horizon (int): Number of days to predict
            external_factors (pd.DataFrame, optional): External factors for prediction period
            
        Returns:
            pd.DataFrame: Prediction results with confidence intervals
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        if self.model_type == 'prophet':
            future = self.model.make_future_dataframe(periods=horizon)
            
            # Add external factors if provided
            if external_factors is not None:
                for feature in self.features:
                    if feature in external_factors.columns:
                        # Align the external factors with future dataframe
                        for i, date in enumerate(future['ds']):
                            if date in external_factors['date'].values:
                                idx = external_factors[external_factors['date'] == date].index[0]
                                future.loc[i, feature] = external_factors.loc[idx, feature]
                            else:
                                future.loc[i, feature] = 0
            
            # Make prediction
            forecast = self.model.predict(future)
            
            # Get only future predictions
            future_forecast = forecast.iloc[-horizon:]
            
            # Rename columns for consistency
            result = future_forecast.rename(columns={
                'ds': 'date',
                'yhat': 'predicted_demand',
                'yhat_lower': 'confidence_lower',
                'yhat_upper': 'confidence_upper'
            })
            
            # Select relevant columns
            result = result[['date', 'predicted_demand', 'confidence_lower', 'confidence_upper']]
            
        else:  # For Random Forest and Neural Network
            # Generate dates for prediction horizon
            last_date = datetime.now().date()
            future_dates = [last_date + timedelta(days=i) for i in range(1, horizon + 1)]
            
            # Create dataframe for predictions
            future_df = pd.DataFrame({'date': future_dates})
            
            # Add time-based features
            future_df['dayofweek'] = pd.DatetimeIndex(future_df['date']).dayofweek
            future_df['month'] = pd.DatetimeIndex(future_df['date']).month
            future_df['year'] = pd.DatetimeIndex(future_df['date']).year
            future_df['is_weekend'] = future_df['dayofweek'].apply(lambda x: 1 if x >= 5 else 0)
            
            # Add external factors if provided
            if external_factors is not None:
                for feature in external_factors.columns:
                    if feature != 'date':
                        future_df = pd.merge(future_df, 
                                           external_factors[['date', feature]], 
                                           on='date', how='left')
                        future_df[feature] = future_df[feature].fillna(0)
            
            # Ensure all required features are present
            for feature in self.features:
                if feature not in future_df.columns and feature != 'date':
                    future_df[feature] = 0
            
            # Ensure feature order matches training data
            feature_df = future_df[self.features]
            
            # Scale features
            scaled_features = self.scaler.transform(feature_df)
            
            # Make predictions
            if self.model_type == 'randomforest':
                predictions = self.model.predict(scaled_features)
                
                # Calculate confidence intervals (using prediction std)
                pred_std = np.std([tree.predict(scaled_features) 
                                  for tree in self.model.estimators_], axis=0)
                lower_bound = predictions - (1.96 * pred_std)
                upper_bound = predictions + (1.96 * pred_std)
                
            else:  # Neural network
                predictions = self.model.predict(scaled_features).flatten()
                
                # Use a fixed percentage for confidence intervals
                pred_std = 0.2 * predictions  # 20% of prediction
                lower_bound = predictions - (1.96 * pred_std)
                upper_bound = predictions + (1.96 * pred_std)
            
            # Create result dataframe
            result = pd.DataFrame({
                'date': future_dates,
                'predicted_demand': predictions,
                'confidence_lower': lower_bound,
                'confidence_upper': upper_bound
            })
        
        # Ensure no negative predictions
        result['predicted_demand'] = result['predicted_demand'].apply(lambda x: max(0, x))
        result['confidence_lower'] = result['confidence_lower'].apply(lambda x: max(0, x))
        
        return result

    def plot_forecast(self, historical_data, forecast_data, title=None):
        """
        Generate a plot of historical data and forecasts.
        
        Args:
            historical_data (pd.DataFrame): Historical demand data
            forecast_data (pd.DataFrame): Forecast data
            title (str, optional): Plot title
            
        Returns:
            matplotlib.figure.Figure: The generated plot figure
        """
        plt.figure(figsize=(12, 6))
        
        # Plot historical data
        if 'quantity' in historical_data.columns:
            plt.plot(historical_data['date'], historical_data['quantity'], 
                   label='Historical Demand', color='blue')
        else:
            plt.plot(historical_data['ds'], historical_data['y'], 
                   label='Historical Demand', color='blue')
        
        # Plot forecast
        plt.plot(forecast_data['date'], forecast_data['predicted_demand'], 
               label='Forecast', color='red')
        
        # Plot confidence interval
        plt.fill_between(forecast_data['date'], 
                        forecast_data['confidence_lower'],
                        forecast_data['confidence_upper'],
                        color='red', alpha=0.2, label='95% Confidence Interval')
        
        # Add labels and title
        plt.xlabel('Date')
        plt.ylabel('Demand')
        if title:
            plt.title(title)
        else:
            plt.title('Demand Forecast')
        
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        return plt.gcf()

class InventoryOptimizer:
    """
    Class for optimizing inventory levels based on demand predictions.
    """
    
    def __init__(self):
        """Initialize the inventory optimizer."""
        pass
    
    def calculate_optimal_stock(self, product, demand_forecast, lead_time=None, service_level=0.95):
        """
        Calculate optimal stock levels based on demand forecasts.
        
        Args:
            product (Product): Product object with current inventory data
            demand_forecast (pd.DataFrame): Demand forecast from predictor
            lead_time (int, optional): Lead time in days, defaults to product's lead time
            service_level (float): Desired service level (0-1)
            
        Returns:
            dict: Optimal stock recommendations
        """
        if lead_time is None:
            lead_time = product.lead_time
        
        # Calculate average daily demand
        avg_daily_demand = demand_forecast['predicted_demand'].mean()
        
        # Calculate demand variability (standard deviation)
        demand_std = demand_forecast['predicted_demand'].std()
        
        # Calculate safety stock using the service level
        # Using a simplified approach based on normal distribution
        z_score = 1.96  # Corresponds to approx. 95% service level
        if service_level == 0.99:
            z_score = 2.58
        elif service_level == 0.90:
            z_score = 1.64
        
        safety_stock = z_score * demand_std * np.sqrt(lead_time)
        
        # Calculate reorder point
        reorder_point = (avg_daily_demand * lead_time) + safety_stock
        
        # Calculate optimal order quantity (Economic Order Quantity)
        # Simplified EOQ assuming fixed order cost and holding cost
        annual_demand = avg_daily_demand * 365
        order_cost = 25  # Fixed cost per order, in currency units
        holding_cost_percent = 0.25  # Annual holding cost as percentage of unit cost
        holding_cost = product.cost * holding_cost_percent
        
        eoq = np.sqrt((2 * annual_demand * order_cost) / holding_cost)
        
        # Calculate optimal stock level
        optimal_stock = reorder_point + eoq
        
        # Round to whole numbers
        safety_stock = round(safety_stock)
        reorder_point = round(reorder_point)
        eoq = round(eoq)
        optimal_stock = round(optimal_stock)
        
        return {
            'product_id': product.id,
            'current_stock': product.current_stock,
            'avg_daily_demand': avg_daily_demand,
            'demand_variability': demand_std,
            'safety_stock': safety_stock,
            'reorder_point': reorder_point,
            'economic_order_quantity': eoq,
            'optimal_stock': optimal_stock,
            'service_level': service_level,
            'lead_time': lead_time
        }
    
    def calculate_stock_costs(self, product, optimal_levels, days=30):
        """
        Calculate costs associated with current and optimal stock levels.
        
        Args:
            product (Product): Product object with current inventory data
            optimal_levels (dict): Output from calculate_optimal_stock
            days (int): Number of days to calculate costs for
            
        Returns:
            dict: Cost analysis
        """
        # Current stock metrics
        current_stock = product.current_stock
        current_reorder = product.reorder_point
        
        # Optimal stock metrics
        optimal_stock = optimal_levels['optimal_stock']
        optimal_reorder = optimal_levels['reorder_point']
        avg_daily_demand = optimal_levels['avg_daily_demand']
        
        # Calculate holding costs
        holding_cost_percent = 0.25 / 365  # Daily holding cost as percentage of unit cost
        current_holding_cost = current_stock * product.cost * holding_cost_percent * days
        optimal_holding_cost = optimal_stock * product.cost * holding_cost_percent * days
        
        # Estimate stockouts with current policy
        # Simplified calculation based on normal distribution
        z_current = (current_reorder - (avg_daily_demand * product.lead_time)) / \
                    (optimal_levels['demand_variability'] * np.sqrt(product.lead_time))
        
        from scipy.stats import norm
        stockout_prob_current = 1 - norm.cdf(z_current)
        expected_stockouts_current = stockout_prob_current * days / product.lead_time
        
        # Stockout costs (assuming lost sales)
        stockout_cost_per_unit = product.price - product.cost
        current_stockout_cost = expected_stockouts_current * avg_daily_demand * stockout_cost_per_unit
        
        # Same calculation for optimal policy
        z_optimal = (optimal_reorder - (avg_daily_demand * product.lead_time)) / \
                    (optimal_levels['demand_variability'] * np.sqrt(product.lead_time))
        stockout_prob_optimal = 1 - norm.cdf(z_optimal)
        expected_stockouts_optimal = stockout_prob_optimal * days / product.lead_time
        optimal_stockout_cost = expected_stockouts_optimal * avg_daily_demand * stockout_cost_per_unit
        
        # Total costs
        current_total_cost = current_holding_cost + current_stockout_cost
        optimal_total_cost = optimal_holding_cost + optimal_stockout_cost
        savings = current_total_cost - optimal_total_cost
        
        return {
            'product_id': product.id,
            'days_analyzed': days,
            'current_policy': {
                'holding_cost': current_holding_cost,
                'stockout_probability': stockout_prob_current,
                'expected_stockouts': expected_stockouts_current,
                'stockout_cost': current_stockout_cost,
                'total_cost': current_total_cost
            },
            'optimal_policy': {
                'holding_cost': optimal_holding_cost,
                'stockout_probability': stockout_prob_optimal,
                'expected_stockouts': expected_stockouts_optimal,
                'stockout_cost': optimal_stockout_cost,
                'total_cost': optimal_total_cost
            },
            'potential_savings': savings,
            'savings_percent': (savings / current_total_cost) * 100 if current_total_cost > 0 else 0
        }

def get_sales_data(db, product_id, start_date=None, end_date=None):
    """
    Retrieve sales data for a product from the database.
    
    Args:
        db: Database session
        product_id (int): Product ID
        start_date (datetime, optional): Start date for data retrieval
        end_date (datetime, optional): End date for data retrieval
        
    Returns:
        pd.DataFrame: Sales data
    """
    from models import Sale
    import sqlalchemy as sa
    
    query = sa.select(Sale).where(Sale.product_id == product_id)
    
    if start_date:
        query = query.where(Sale.date >= start_date)
    if end_date:
        query = query.where(Sale.date <= end_date)
    
    # Execute query
    sales = db.session.execute(query).scalars().all()
    
    # Convert to DataFrame
    sales_data = pd.DataFrame([
        {
            'date': sale.date,
            'quantity': sale.quantity,
            'unit_price': sale.unit_price,
            'total_price': sale.total_price,
            'channel': sale.channel
        }
        for sale in sales
    ])
    
    return sales_data

def get_external_factors(db, start_date=None, end_date=None):
    """
    Retrieve external factors data from the database.
    
    Args:
        db: Database session
        start_date (datetime, optional): Start date for data retrieval
        end_date (datetime, optional): End date for data retrieval
        
    Returns:
        pd.DataFrame: External factors data
    """
    from models import ExternalFactor
    import sqlalchemy as sa
    
    query = sa.select(ExternalFactor)
    
    if start_date:
        query = query.where(ExternalFactor.date >= start_date)
    if end_date:
        query = query.where(ExternalFactor.date <= end_date)
    
    # Execute query
    factors = db.session.execute(query).scalars().all()
    
    # Convert to DataFrame
    factors_data = pd.DataFrame([
        {
            'date': factor.date,
            'name': factor.name,
            'impact_level': factor.impact_level,
            'category': factor.category
        }
        for factor in factors
    ])
    
    # Pivot the data to get one column per factor type
    if not factors_data.empty:
        # Create pivot for weather
        weather_pivot = factors_data[factors_data['category'] == 'weather'].pivot_table(
            index='date', columns='name', values='impact_level', aggfunc='mean'
        ).reset_index()
        weather_pivot.columns = ['date'] + [f'weather_{col}' for col in weather_pivot.columns if col != 'date']
        
        # Create pivot for holidays
        holiday_pivot = factors_data[factors_data['category'] == 'holiday'].pivot_table(
            index='date', columns='name', values='impact_level', aggfunc='mean'
        ).reset_index()
        holiday_pivot.columns = ['date'] + [f'holiday_{col}' for col in holiday_pivot.columns if col != 'date']
        
        # Create pivot for promotions
        promotion_pivot = factors_data[factors_data['category'] == 'promotion'].pivot_table(
            index='date', columns='name', values='impact_level', aggfunc='mean'
        ).reset_index()
        promotion_pivot.columns = ['date'] + [f'promo_{col}' for col in promotion_pivot.columns if col != 'date']
        
        # Merge all pivots
        result = weather_pivot
        for df in [holiday_pivot, promotion_pivot]:
            if 'date' in df.columns:  # Ensure the dataframe is not empty
                result = pd.merge(result, df, on='date', how='outer')
        
        # Fill NaN values with 0
        result = result.fillna(0)
        
        return result
    
    return pd.DataFrame()

def generate_inventory_report(db, product_id=None, category_id=None):
    """
    Generate a comprehensive inventory report.
    
    Args:
        db: Database session
        product_id (int, optional): Filter by specific product
        category_id (int, optional): Filter by category
        
    Returns:
        dict: Inventory report data
    """
    from models import Product, Category, Sale, InventoryChange
    import sqlalchemy as sa
    
    # Base query
    query = sa.select(Product)
    
    # Apply filters
    if product_id:
        query = query.where(Product.id == product_id)
    if category_id:
        query = query.where(Product.category_id == category_id)
    
    # Execute query
    products = db.session.execute(query).scalars().all()
    
    # Prepare report
    report = {
        'generated_at': datetime.now(),
        'total_products': len(products),
        'total_value': sum(p.current_stock * p.price for p in products),
        'total_cost': sum(p.current_stock * p.cost for p in products),
        'products': []
    }
    
    # Add product details
    for product in products:
        # Get recent sales
        sales_query = sa.select(
            sa.func.sum(Sale.quantity).label('total_quantity'),
            sa.func.sum(Sale.total_price).label('total_revenue')
        ).where(
            Sale.product_id == product.id,
            Sale.date >= datetime.now() - timedelta(days=30)
        )
        sales_result = db.session.execute(sales_query).one()
        
        # Get recent inventory changes
        changes_query = sa.select(InventoryChange).where(
            InventoryChange.product_id == product.id,
            InventoryChange.date >= datetime.now() - timedelta(days=30)
        ).order_by(InventoryChange.date.desc())
        changes = db.session.execute(changes_query).scalars().all()
        
        product_report = {
            'id': product.id,
            'name': product.name,
            'sku': product.sku,
            'category': product.category.name if product.category else 'Uncategorized',
            'current_stock': product.current_stock,
            'reorder_point': product.reorder_point,
            'optimal_stock': product.optimal_stock,
            'stock_status': product.stock_status(),
            'value': product.current_stock * product.price,
            'cost': product.current_stock * product.cost,
            'margin': (product.price - product.cost) / product.price if product.price > 0 else 0,
            'recent_sales': {
                'quantity': sales_result.total_quantity or 0,
                'revenue': sales_result.total_revenue or 0
            },
            'recent_changes': [
                {
                    'date': change.date,
                    'quantity_change': change.quantity_change,
                    'reason': change.reason
                }
                for change in changes[:5]  # Limit to 5 most recent changes
            ]
        }
        
        report['products'].append(product_report)
    
    # Sort products by value (descending)
    report['products'] = sorted(
        report['products'], 
        key=lambda p: p['value'], 
        reverse=True
    )
    
    return report
