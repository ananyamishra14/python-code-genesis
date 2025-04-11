
"""
Data Generator for Smart Inventory & Demand Prediction System.

This script generates synthetic data for testing and demonstrating
the inventory management and demand prediction features.
"""

import os
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from faker import Faker
import json
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

# Initialize Faker
fake = Faker()

def create_database(db_path="inventory.db"):
    """Create a SQLite database with initial schema."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables based on model definitions
    # User table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT NOT NULL,
        is_contractor BOOLEAN DEFAULT FALSE,
        skills TEXT,
        bio TEXT,
        profile_image TEXT,
        stripe_customer_id TEXT,
        stripe_connect_id TEXT,
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Categories table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS category (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        parent_id INTEGER,
        FOREIGN KEY (parent_id) REFERENCES category (id)
    )
    ''')
    
    # Products table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS product (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        sku TEXT UNIQUE NOT NULL,
        category_id INTEGER,
        price REAL NOT NULL,
        cost REAL NOT NULL,
        current_stock INTEGER DEFAULT 0,
        reorder_point INTEGER DEFAULT 10,
        optimal_stock INTEGER,
        lead_time INTEGER DEFAULT 7,
        is_active BOOLEAN DEFAULT TRUE,
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES category (id)
    )
    ''')
    
    # Sales table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sale (
        id INTEGER PRIMARY KEY,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        total_price REAL NOT NULL,
        date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        channel TEXT,
        customer_id INTEGER,
        FOREIGN KEY (product_id) REFERENCES product (id)
    )
    ''')
    
    # Inventory Changes table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory_change (
        id INTEGER PRIMARY KEY,
        product_id INTEGER NOT NULL,
        quantity_change INTEGER NOT NULL,
        reason TEXT NOT NULL,
        reference_id TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user_id INTEGER,
        FOREIGN KEY (product_id) REFERENCES product (id),
        FOREIGN KEY (user_id) REFERENCES user (id)
    )
    ''')
    
    # External Factors table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS external_factor (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        date DATE NOT NULL,
        impact_level REAL,
        category TEXT,
        data TEXT
    )
    ''')
    
    # Predictions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS prediction (
        id INTEGER PRIMARY KEY,
        product_id INTEGER NOT NULL,
        date DATE NOT NULL,
        predicted_demand REAL NOT NULL,
        confidence_lower REAL,
        confidence_upper REAL,
        factors TEXT,
        model_version TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES product (id)
    )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"Database created at {db_path}")

def generate_users(db_path, num_users=5):
    """Generate fake users and store in the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Generate admin user
    admin_user = {
        "email": "admin@example.com",
        "password": "$2b$12$FriM5uU/pVvPVUgQtqYtZOGrwpQRoLEEGHeorFbCXrfBxDzJf.uZm",  # hashed 'password123'
        "name": "Admin User",
        "is_contractor": False,
        "skills": None,
        "bio": "System administrator",
        "profile_image": None,
        "stripe_customer_id": f"cus_{fake.uuid4()[:8]}",
        "stripe_connect_id": None
    }
    
    cursor.execute('''
    INSERT INTO user (email, password, name, is_contractor, skills, bio, 
                     profile_image, stripe_customer_id, stripe_connect_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        admin_user["email"], admin_user["password"], admin_user["name"], 
        admin_user["is_contractor"], admin_user["skills"], admin_user["bio"],
        admin_user["profile_image"], admin_user["stripe_customer_id"], 
        admin_user["stripe_connect_id"]
    ))
    
    # Generate regular users
    for _ in range(num_users - 1):
        is_contractor = random.choice([True, False])
        user = {
            "email": fake.email(),
            "password": "$2b$12$FriM5uU/pVvPVUgQtqYtZOGrwpQRoLEEGHeorFbCXrfBxDzJf.uZm",  # hashed 'password123'
            "name": fake.name(),
            "is_contractor": is_contractor,
            "skills": ", ".join(random.sample(["Web Development", "Marketing", "Design", "SEO", "Data Analysis", "Copywriting"], k=random.randint(1, 3))) if is_contractor else None,
            "bio": fake.paragraph(nb_sentences=3) if random.random() > 0.5 else None,
            "profile_image": None,
            "stripe_customer_id": f"cus_{fake.uuid4()[:8]}",
            "stripe_connect_id": f"acct_{fake.uuid4()[:8]}" if is_contractor else None
        }
        
        cursor.execute('''
        INSERT INTO user (email, password, name, is_contractor, skills, bio, 
                         profile_image, stripe_customer_id, stripe_connect_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user["email"], user["password"], user["name"], 
            user["is_contractor"], user["skills"], user["bio"],
            user["profile_image"], user["stripe_customer_id"], 
            user["stripe_connect_id"]
        ))
    
    conn.commit()
    conn.close()
    
    print(f"Generated {num_users} users")

def generate_categories(db_path):
    """Generate product categories."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Main categories
    main_categories = [
        {
            "name": "Electronics",
            "description": "Electronic devices and accessories",
        },
        {
            "name": "Clothing",
            "description": "Apparel for men, women, and children",
        },
        {
            "name": "Home & Kitchen",
            "description": "Products for home and kitchen use",
        },
        {
            "name": "Sports & Outdoors",
            "description": "Athletic and outdoor recreation equipment",
        },
        {
            "name": "Beauty & Personal Care",
            "description": "Beauty products and personal care items",
        }
    ]
    
    main_category_ids = {}
    for category in main_categories:
        cursor.execute('''
        INSERT INTO category (name, description, parent_id)
        VALUES (?, ?, ?)
        ''', (category["name"], category["description"], None))
        main_category_ids[category["name"]] = cursor.lastrowid
    
    # Subcategories
    subcategories = [
        {
            "name": "Smartphones",
            "description": "Mobile phones and accessories",
            "parent": "Electronics"
        },
        {
            "name": "Laptops",
            "description": "Portable computers",
            "parent": "Electronics"
        },
        {
            "name": "Audio",
            "description": "Headphones, speakers, and audio equipment",
            "parent": "Electronics"
        },
        {
            "name": "Men's Clothing",
            "description": "Apparel for men",
            "parent": "Clothing"
        },
        {
            "name": "Women's Clothing",
            "description": "Apparel for women",
            "parent": "Clothing"
        },
        {
            "name": "Kids' Clothing",
            "description": "Apparel for children",
            "parent": "Clothing"
        },
        {
            "name": "Kitchen Appliances",
            "description": "Appliances for kitchen use",
            "parent": "Home & Kitchen"
        },
        {
            "name": "Furniture",
            "description": "Home and office furniture",
            "parent": "Home & Kitchen"
        },
        {
            "name": "Fitness Equipment",
            "description": "Exercise and fitness gear",
            "parent": "Sports & Outdoors"
        },
        {
            "name": "Outdoor Recreation",
            "description": "Camping, hiking, and outdoor activities",
            "parent": "Sports & Outdoors"
        },
        {
            "name": "Skincare",
            "description": "Facial and body skincare products",
            "parent": "Beauty & Personal Care"
        },
        {
            "name": "Haircare",
            "description": "Shampoo, conditioner, and styling products",
            "parent": "Beauty & Personal Care"
        }
    ]
    
    for subcategory in subcategories:
        parent_id = main_category_ids.get(subcategory["parent"])
        cursor.execute('''
        INSERT INTO category (name, description, parent_id)
        VALUES (?, ?, ?)
        ''', (subcategory["name"], subcategory["description"], parent_id))
    
    conn.commit()
    conn.close()
    
    print(f"Generated {len(main_categories)} main categories and {len(subcategories)} subcategories")

def generate_products(db_path, num_products=50):
    """Generate products and store in the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get categories
    cursor.execute("SELECT id, name FROM category WHERE parent_id IS NOT NULL")
    subcategories = cursor.fetchall()
    
    # Sample product types by category
    product_types = {
        "Smartphones": ["iPhone", "Samsung Galaxy", "Google Pixel", "OnePlus"],
        "Laptops": ["MacBook", "Dell XPS", "HP Spectre", "Lenovo ThinkPad"],
        "Audio": ["Wireless Earbuds", "Bluetooth Speaker", "Headphones", "Soundbar"],
        "Men's Clothing": ["T-Shirt", "Jeans", "Jacket", "Sweater"],
        "Women's Clothing": ["Dress", "Blouse", "Skirt", "Jeans"],
        "Kids' Clothing": ["T-Shirt", "Pants", "Jacket", "Sweater"],
        "Kitchen Appliances": ["Blender", "Coffee Maker", "Toaster", "Microwave"],
        "Furniture": ["Desk", "Chair", "Sofa", "Bookshelf"],
        "Fitness Equipment": ["Yoga Mat", "Dumbbells", "Resistance Bands", "Exercise Bike"],
        "Outdoor Recreation": ["Tent", "Sleeping Bag", "Hiking Backpack", "Camping Stove"],
        "Skincare": ["Moisturizer", "Facial Cleanser", "Serum", "Sunscreen"],
        "Haircare": ["Shampoo", "Conditioner", "Hair Mask", "Styling Gel"]
    }
    
    # Generate products
    products = []
    for _ in range(num_products):
        # Select random subcategory
        category_id, category_name = random.choice(subcategories)
        
        # Get product types for this category
        category_product_types = product_types.get(category_name, ["Generic Item"])
        product_type = random.choice(category_product_types)
        
        # Generate product details
        price = round(random.uniform(9.99, 999.99), 2)
        markup = random.uniform(1.3, 2.5)  # 30% to 150% markup
        cost = round(price / markup, 2)
        
        current_stock = random.randint(0, 200)
        reorder_point = random.randint(5, 50)
        optimal_stock = reorder_point * random.randint(2, 4)
        lead_time = random.randint(3, 30)
        
        product = {
            "name": f"{fake.company()} {product_type}",
            "description": fake.paragraph(nb_sentences=3),
            "sku": f"{category_name[:3].upper()}-{fake.unique.random_int(min=100, max=999)}",
            "category_id": category_id,
            "price": price,
            "cost": cost,
            "current_stock": current_stock,
            "reorder_point": reorder_point,
            "optimal_stock": optimal_stock,
            "lead_time": lead_time,
            "is_active": True
        }
        
        cursor.execute('''
        INSERT INTO product (name, description, sku, category_id, price, cost,
                           current_stock, reorder_point, optimal_stock, lead_time, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            product["name"], product["description"], product["sku"], product["category_id"],
            product["price"], product["cost"], product["current_stock"], product["reorder_point"],
            product["optimal_stock"], product["lead_time"], product["is_active"]
        ))
        
        product["id"] = cursor.lastrowid
        products.append(product)
    
    conn.commit()
    conn.close()
    
    print(f"Generated {num_products} products")
    return products

def generate_sales_data(db_path, products, days=180):
    """Generate historical sales data for products."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Generate sales for each product
    total_sales = 0
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Channels
    channels = ["in-store", "online", "wholesale", "marketplace"]
    
    # Holiday effects
    holidays = {
        # Date: (Name, Impact Factor)
        # Impact Factor > 1 means increased sales
        "2023-01-01": ("New Year's Day", 1.2),
        "2023-02-14": ("Valentine's Day", 1.5),
        "2023-05-29": ("Memorial Day", 1.3),
        "2023-07-04": ("Independence Day", 1.2),
        "2023-09-04": ("Labor Day", 1.3),
        "2023-10-31": ("Halloween", 1.4),
        "2023-11-24": ("Black Friday", 2.5),
        "2023-11-27": ("Cyber Monday", 2.0),
        "2023-12-24": ("Christmas Eve", 1.8),
        "2023-12-25": ("Christmas", 0.5),  # Low sales on Christmas Day
        "2023-12-31": ("New Year's Eve", 1.1)
    }
    
    # Generate sales for each product
    for product in products:
        # Base parameters for this product
        base_daily_demand = random.uniform(1, 10)  # Average daily sales
        seasonality_amplitude = random.uniform(0.1, 0.5)  # Strength of seasonal effect
        trend_slope = random.uniform(-0.01, 0.03)  # Upward or downward trend
        noise_level = random.uniform(0.1, 0.4)  # Randomness in sales
        
        # Generate daily sales
        current_date = start_date
        day_index = 0
        
        while current_date <= end_date:
            # Apply trend
            trend_effect = 1 + trend_slope * day_index
            
            # Apply seasonality (weekly and annual)
            weekly_effect = 1 + 0.3 * seasonality_amplitude * np.sin(2 * np.pi * current_date.weekday() / 7)
            annual_effect = 1 + seasonality_amplitude * np.sin(2 * np.pi * current_date.timetuple().tm_yday / 365)
            
            # Determine if it's a holiday
            holiday_effect = 1.0
            holiday_name = None
            date_str = current_date.strftime("%Y-%m-%d")
            if date_str in holidays:
                holiday_name, holiday_effect = holidays[date_str]
            
            # Calculate expected demand
            expected_demand = base_daily_demand * trend_effect * weekly_effect * annual_effect * holiday_effect
            
            # Add random noise
            actual_demand = max(0, np.random.normal(expected_demand, noise_level * expected_demand))
            
            # Round to integer quantity
            quantity = int(actual_demand)
            
            if quantity > 0:
                # Apply small random price variation
                unit_price = product["price"] * random.uniform(0.95, 1.05)
                unit_price = round(unit_price, 2)
                total_price = round(unit_price * quantity, 2)
                
                # Select channel
                channel = random.choice(channels)
                
                # Random customer ID (can be null)
                customer_id = random.randint(1, 1000) if random.random() > 0.3 else None
                
                # Insert sale
                cursor.execute('''
                INSERT INTO sale (product_id, quantity, unit_price, total_price, date, channel, customer_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    product["id"], quantity, unit_price, total_price, 
                    current_date.strftime("%Y-%m-%d %H:%M:%S"),
                    channel, customer_id
                ))
                
                total_sales += 1
                
                # Update inventory for each sale
                cursor.execute('''
                INSERT INTO inventory_change 
                (product_id, quantity_change, reason, reference_id, date)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    product["id"], -quantity, "sale", f"sale_{cursor.lastrowid}",
                    current_date.strftime("%Y-%m-%d %H:%M:%S")
                ))
            
            # Occasionally add inventory restocks
            if product["current_stock"] < product["reorder_point"] and random.random() < 0.3:
                restock_quantity = random.randint(
                    product["optimal_stock"] - product["current_stock"],
                    product["optimal_stock"] * 2 - product["current_stock"]
                )
                
                if restock_quantity > 0:
                    restock_date = current_date + timedelta(days=random.randint(1, product["lead_time"]))
                    
                    if restock_date <= end_date:
                        cursor.execute('''
                        INSERT INTO inventory_change 
                        (product_id, quantity_change, reason, reference_id, date)
                        VALUES (?, ?, ?, ?, ?)
                        ''', (
                            product["id"], restock_quantity, "restock", f"po_{fake.uuid4()[:8]}",
                            restock_date.strftime("%Y-%m-%d %H:%M:%S")
                        ))
            
            current_date += timedelta(days=1)
            day_index += 1
    
    # Update current stock based on inventory changes
    cursor.execute('''
    UPDATE product 
    SET current_stock = (
        SELECT COALESCE(SUM(quantity_change), 0) + product.current_stock
        FROM inventory_change
        WHERE inventory_change.product_id = product.id
    )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"Generated {total_sales} sales records across {days} days")

def generate_external_factors(db_path, days=180):
    """Generate external factors data such as weather, holidays, promotions."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Generate factors for the past X days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Weather factors
    weather_types = ["temperature", "precipitation", "is_weekend"]
    
    # Holiday data
    holidays = {
        # Date: (Name, Impact Factor)
        "2023-01-01": ("New Year's Day", 0.8),
        "2023-02-14": ("Valentine's Day", 0.9),
        "2023-05-29": ("Memorial Day", 0.7),
        "2023-07-04": ("Independence Day", 0.6),
        "2023-09-04": ("Labor Day", 0.7),
        "2023-10-31": ("Halloween", 0.8),
        "2023-11-24": ("Black Friday", 1.0),
        "2023-11-27": ("Cyber Monday", 0.9),
        "2023-12-24": ("Christmas Eve", 0.9),
        "2023-12-25": ("Christmas", 0.2),
        "2023-12-31": ("New Year's Eve", 0.7)
    }
    
    # Promotion data
    promotion_types = ["discount", "BOGO", "flash_sale", "clearance"]
    
    # Generate data for each day
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        
        # Weather data
        # Temperature (normalized to -1 to 1 range)
        # Higher in summer, lower in winter (Northern Hemisphere)
        day_of_year = current_date.timetuple().tm_yday
        base_temp = np.sin(2 * np.pi * (day_of_year - 172) / 365)  # Peak at day 172 (summer)
        temp_with_noise = base_temp + np.random.normal(0, 0.2)
        temp_impact = min(1, max(-1, temp_with_noise))
        
        cursor.execute('''
        INSERT INTO external_factor (name, description, date, impact_level, category, data)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            "temperature", "Daily temperature normalized to -1 to 1 scale",
            date_str, temp_impact, "weather", json.dumps({"value": temp_impact})
        ))
        
        # Precipitation (0 to 1, with occasional spikes)
        if random.random() < 0.3:  # 30% chance of precipitation
            precip_level = random.uniform(0.2, 1.0)
            precip_impact = -precip_level * 0.5  # Negative impact on sales
            
            cursor.execute('''
            INSERT INTO external_factor (name, description, date, impact_level, category, data)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                "precipitation", "Precipitation level (0-1)",
                date_str, precip_impact, "weather", json.dumps({"value": precip_level})
            ))
        
        # Weekend factor
        is_weekend = 1 if current_date.weekday() >= 5 else 0
        weekend_impact = 0.3 if is_weekend else 0
        
        cursor.execute('''
        INSERT INTO external_factor (name, description, date, impact_level, category, data)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            "is_weekend", "Weekend flag (0 or 1)",
            date_str, weekend_impact, "weather", json.dumps({"value": is_weekend})
        ))
        
        # Holiday factor
        if date_str in holidays:
            holiday_name, holiday_impact = holidays[date_str]
            
            cursor.execute('''
            INSERT INTO external_factor (name, description, date, impact_level, category, data)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                holiday_name, f"Holiday: {holiday_name}",
                date_str, holiday_impact, "holiday", json.dumps({"name": holiday_name})
            ))
        
        # Random promotions (10% chance per day)
        if random.random() < 0.1:
            promo_type = random.choice(promotion_types)
            promo_impact = random.uniform(0.3, 0.8)
            
            cursor.execute('''
            INSERT INTO external_factor (name, description, date, impact_level, category, data)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                promo_type, f"Promotion: {promo_type.replace('_', ' ').title()}",
                date_str, promo_impact, "promotion", 
                json.dumps({"type": promo_type, "discount": random.randint(10, 50)})
            ))
        
        current_date += timedelta(days=1)
    
    conn.commit()
    conn.close()
    
    print(f"Generated external factors data for {days} days")

def generate_sample_predictions(db_path, num_products=10, days_to_predict=30):
    """Generate sample predictions for selected products."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get top products by sales volume
    cursor.execute('''
    SELECT product_id, SUM(quantity) as total_quantity
    FROM sale
    GROUP BY product_id
    ORDER BY total_quantity DESC
    LIMIT ?
    ''', (num_products,))
    
    top_products = cursor.fetchall()
    
    # Generate predictions for each product
    start_date = datetime.now().date()
    model_version = "prophet-1.0"
    
    for product_id, _ in top_products:
        # Get product details
        cursor.execute("SELECT name FROM product WHERE id = ?", (product_id,))
        product_name = cursor.fetchone()[0]
        
        # Get recent sales data for this product
        cursor.execute('''
        SELECT date, SUM(quantity) as daily_quantity
        FROM sale
        WHERE product_id = ?
        GROUP BY date(date)
        ORDER BY date DESC
        LIMIT 30
        ''', (product_id,))
        
        recent_sales = cursor.fetchall()
        
        if recent_sales:
            # Calculate average and std dev of recent sales
            quantities = [q for _, q in recent_sales]
            avg_quantity = sum(quantities) / len(quantities)
            std_dev = (sum((q - avg_quantity) ** 2 for q in quantities) / len(quantities)) ** 0.5
            
            # Generate predictions with increasing uncertainty
            for i in range(days_to_predict):
                prediction_date = start_date + timedelta(days=i)
                
                # Base prediction on average with some trend
                trend_factor = 1 + (i / 100) * random.choice([-1, 1])  # Small up or down trend
                
                # Add day of week seasonality
                day_of_week = prediction_date.weekday()
                day_factors = {
                    0: 0.9,    # Monday
                    1: 0.95,   # Tuesday
                    2: 1.0,    # Wednesday
                    3: 1.05,   # Thursday
                    4: 1.2,    # Friday
                    5: 1.3,    # Saturday
                    6: 1.1     # Sunday
                }
                day_factor = day_factors.get(day_of_week, 1.0)
                
                # Calculate predicted demand
                predicted_demand = avg_quantity * trend_factor * day_factor
                
                # Increase uncertainty with time
                uncertainty_factor = 1 + (i / 10)
                confidence_interval = std_dev * uncertainty_factor
                
                # Insert prediction
                cursor.execute('''
                INSERT INTO prediction 
                (product_id, date, predicted_demand, confidence_lower, confidence_upper, 
                factors, model_version)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    product_id, prediction_date.strftime("%Y-%m-%d"), 
                    predicted_demand, max(0, predicted_demand - confidence_interval),
                    predicted_demand + confidence_interval,
                    json.dumps({
                        "trend_factor": trend_factor,
                        "day_factor": day_factor,
                        "uncertainty": uncertainty_factor
                    }),
                    model_version
                ))
            
            print(f"Generated {days_to_predict} predictions for {product_name}")
    
    conn.commit()
    conn.close()
    
    print(f"Generated predictions for {len(top_products)} products")

def create_sales_visualization(db_path, output_dir="visualizations"):
    """Create visualizations of sales data."""
    conn = sqlite3.connect(db_path)
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Get sales by date
    sales_by_date = pd.read_sql_query('''
    SELECT date(date) as sale_date, SUM(quantity) as total_quantity, 
           SUM(total_price) as total_revenue
    FROM sale
    GROUP BY date(date)
    ORDER BY date(date)
    ''', conn)
    
    # Plot sales trend
    plt.figure(figsize=(12, 6))
    plt.plot(pd.to_datetime(sales_by_date['sale_date']), sales_by_date['total_quantity'], 
             marker='o', linestyle='-', markersize=3)
    plt.title('Daily Sales Volume Over Time')
    plt.xlabel('Date')
    plt.ylabel('Units Sold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'daily_sales_volume.png'))
    
    # Plot revenue trend
    plt.figure(figsize=(12, 6))
    plt.plot(pd.to_datetime(sales_by_date['sale_date']), sales_by_date['total_revenue'], 
             marker='o', linestyle='-', markersize=3, color='green')
    plt.title('Daily Revenue Over Time')
    plt.xlabel('Date')
    plt.ylabel('Revenue ($)')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'daily_revenue.png'))
    
    # Get sales by category
    sales_by_category = pd.read_sql_query('''
    SELECT c.name as category, SUM(s.quantity) as total_quantity, 
           SUM(s.total_price) as total_revenue
    FROM sale s
    JOIN product p ON s.product_id = p.id
    JOIN category c ON p.category_id = c.id
    GROUP BY c.name
    ORDER BY total_revenue DESC
    ''', conn)
    
    # Plot sales by category
    plt.figure(figsize=(12, 6))
    plt.bar(sales_by_category['category'], sales_by_category['total_quantity'], color='skyblue')
    plt.title('Sales Volume by Category')
    plt.xlabel('Category')
    plt.ylabel('Units Sold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'sales_by_category.png'))
    
    # Plot revenue by category
    plt.figure(figsize=(12, 6))
    plt.bar(sales_by_category['category'], sales_by_category['total_revenue'], color='lightgreen')
    plt.title('Revenue by Category')
    plt.xlabel('Category')
    plt.ylabel('Revenue ($)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'revenue_by_category.png'))
    
    # Get top products
    top_products = pd.read_sql_query('''
    SELECT p.name as product_name, SUM(s.quantity) as total_quantity, 
           SUM(s.total_price) as total_revenue
    FROM sale s
    JOIN product p ON s.product_id = p.id
    GROUP BY p.name
    ORDER BY total_revenue DESC
    LIMIT 10
    ''', conn)
    
    # Plot top products by revenue
    plt.figure(figsize=(12, 6))
    plt.barh(top_products['product_name'], top_products['total_revenue'], color='coral')
    plt.title('Top 10 Products by Revenue')
    plt.xlabel('Revenue ($)')
    plt.ylabel('Product')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'top_products_revenue.png'))
    
    # Plot sales by channel
    sales_by_channel = pd.read_sql_query('''
    SELECT channel, SUM(quantity) as total_quantity, SUM(total_price) as total_revenue
    FROM sale
    GROUP BY channel
    ORDER BY total_revenue DESC
    ''', conn)
    
    plt.figure(figsize=(10, 6))
    plt.pie(sales_by_channel['total_revenue'], labels=sales_by_channel['channel'], 
            autopct='%1.1f%%', startangle=90, shadow=True)
    plt.title('Revenue by Sales Channel')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'sales_by_channel.png'))
    
    # Weekly sales pattern
    weekly_pattern = pd.read_sql_query('''
    SELECT strftime('%w', date) as day_of_week, SUM(quantity) as total_quantity
    FROM sale
    GROUP BY day_of_week
    ORDER BY day_of_week
    ''', conn)
    
    day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    weekly_pattern['day_name'] = weekly_pattern['day_of_week'].astype(int).apply(lambda x: day_names[x])
    
    plt.figure(figsize=(10, 6))
    plt.bar(weekly_pattern['day_name'], weekly_pattern['total_quantity'], color='purple')
    plt.title('Weekly Sales Pattern')
    plt.xlabel('Day of Week')
    plt.ylabel('Units Sold')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'weekly_sales_pattern.png'))
    
    conn.close()
    
    print(f"Generated visualizations in {output_dir} directory")

if __name__ == "__main__":
    db_path = "inventory.db"
    
    # Create the database and schema
    create_database(db_path)
    
    # Generate data
    generate_users(db_path, num_users=10)
    generate_categories(db_path)
    products = generate_products(db_path, num_products=50)
    generate_sales_data(db_path, products, days=180)
    generate_external_factors(db_path, days=180)
    generate_sample_predictions(db_path, num_products=10, days_to_predict=30)
    
    # Create visualizations
    create_sales_visualization(db_path)
    
    print("Data generation complete!")
