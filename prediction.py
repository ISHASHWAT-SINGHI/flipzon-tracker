import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import sqlite3

def predict_best_time(product_id):
    """Predict best time to buy with price forecasting"""
    conn = sqlite3.connect('price_history.db')
    
    # Load historical data
    query = f'''
    SELECT p.timestamp, p.price, p.available, p.source,
           strftime('%w', p.timestamp) as weekday,
           strftime('%m', p.timestamp) as month
    FROM prices p
    WHERE p.product_id = '{product_id}'
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if len(df) < 15:
        return "Insufficient data (need 15+ records)", None, None
    
    # Feature engineering
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.sort_values('timestamp', inplace=True)
    df['days'] = (df['timestamp'] - df['timestamp'].min()).dt.days
    
    # Encode categorical features
    le = LabelEncoder()
    df['source_encoded'] = le.fit_transform(df['source'])
    
    # Prepare data
    X = df[['days', 'weekday', 'month', 'source_encoded']]
    y = df['price']
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    
    # Forecast next 14 days
    last_date = df['timestamp'].max()
    future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, 15)]
    
    future_df = pd.DataFrame({
        'timestamp': future_dates,
        'days': (future_dates - df['timestamp'].min()).days,
        'weekday': [d.strftime('%w') for d in future_dates],
        'month': [d.strftime('%m') for d in future_dates]
    })
    
    # Predict using most common source
    common_source = df['source'].mode()[0]
    future_df['source_encoded'] = le.transform([common_source] * 14)
    
    future_df['predicted_price'] = model.predict(future_df[['days', 'weekday', 'month', 'source_encoded']])
    
    # Find best buying day
    best_day = future_df.loc[future_df['predicted_price'].idxmin()]
    
    return {
        'best_date': best_day['timestamp'].strftime('%Y-%m-%d'),
        'predicted_price': round(best_day['predicted_price'], 2),
        'current_price': df.iloc[-1]['price'],
        'accuracy': f"MAE: ₹{mae:.2f}",
        'forecast': future_df[['timestamp', 'predicted_price']].to_dict('records')
    }