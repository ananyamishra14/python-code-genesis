
# Smart Inventory & Demand Prediction System

A comprehensive inventory management system that uses machine learning and AI to predict demand, optimize stock levels, and provide real-time analytics for retail businesses.

## Project Overview

This Smart Inventory & Demand Prediction System addresses common retail challenges like overstocking and understocking by implementing advanced machine learning algorithms that analyze historical sales data and external factors to accurately predict future demand.

### Key Features

- **AI-Powered Demand Prediction**: Uses multiple ML models including Prophet, LSTM, and Random Forest
- **Smart Inventory Optimization**: Automatically calculates optimal reorder points and stock levels
- **External Factor Analysis**: Considers holidays, weather, promotions, and seasonality 
- **Real-time Analytics Dashboard**: Visualizes sales trends, inventory status, and predictions
- **Cost Optimization**: Reduces holding costs while minimizing stockouts through data-driven recommendations

## Tech Stack

- **Backend**: Python with Flask
- **Database**: SQLAlchemy with SQLite (configurable for production databases)
- **ML & AI**: TensorFlow, Prophet, Scikit-learn for prediction models
- **Data Analysis**: Pandas, NumPy for data processing
- **Frontend**: React with modern UI components (Tailwind CSS)
- **Visualization**: Recharts for interactive charts and data visualization
- **Payment Processing**: Stripe integration for e-commerce capabilities

## Project Structure

- `app.py`: Main application file with Flask routes and core functionality
- `models.py`: Database models and schema
- `prediction_utils.py`: ML utilities for demand forecasting and inventory optimization
- `endpoints.py`: API endpoints for the frontend to consume
- `data_generator.py`: Tool to generate synthetic data for testing
- `src/components/`: React components for the frontend user interface

## How It Works

1. **Data Collection**: The system collects and stores historical sales data and inventory movements
2. **Demand Prediction**: AI models analyze patterns and external factors to predict future demand
3. **Inventory Optimization**: The system calculates optimal reorder points and stock levels based on predictions
4. **Cost Analysis**: Advanced algorithms calculate potential savings from improved inventory management
5. **Actionable Insights**: The system provides specific recommendations for inventory decisions

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js and npm/yarn for frontend development
- OpenAI API key (optional, for enhanced predictions)
- Stripe API keys (optional, for payment processing)

### Installation

1. Clone the repository
   ```
   git clone https://github.com/yourusername/smart-inventory-system.git
   cd smart-inventory-system
   ```

2. Create a virtual environment
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install backend dependencies
   ```
   pip install -r requirements.txt
   ```

4. Initialize the database
   ```
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

5. Generate sample data (optional)
   ```
   python data_generator.py
   ```

6. Install frontend dependencies
   ```
   cd frontend
   npm install
   ```

7. Set up environment variables
   ```
   export FLASK_APP=app.py
   export FLASK_ENV=development
   export OPENAI_API_KEY=your_openai_api_key  # Optional
   export STRIPE_SECRET_KEY=your_stripe_secret_key  # Optional
   export STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret  # Optional
   ```

8. Run the application
   ```
   flask run
   ```

9. In a separate terminal, run the frontend
   ```
   cd frontend
   npm start
   ```

## AI Models

The system supports multiple prediction models:

- **Prophet**: Facebook's time series forecasting model, excellent for seasonal patterns
- **LSTM Neural Networks**: Deep learning for complex patterns and long-term dependencies
- **Random Forest**: Robust model for handling various factors and categorical features
- **Ensemble Model**: Combines multiple models for improved accuracy

## External Factor Analysis

The system can incorporate various external factors that impact demand:

- **Seasonal Patterns**: Weekly, monthly, and yearly cycles
- **Holidays & Events**: Impact of holidays on consumer behavior
- **Weather Conditions**: How weather affects purchasing patterns
- **Promotions**: Effect of marketing campaigns and discounts
- **Competitor Actions**: Response to competitor pricing and promotions

## Future Enhancements

- **Advanced Neural Networks**: Implementation of more sophisticated deep learning models
- **Blockchain Integration**: Improved supply chain visibility with blockchain technology
- **IoT Integration**: Real-time inventory tracking with IoT devices
- **Computer Vision**: Shelf monitoring and automatic reordering
- **Voice Assistants**: Voice-controlled inventory management

## License

This project is licensed under the MIT License - see the LICENSE file for details.
