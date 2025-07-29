import sqlite3
from datetime import datetime

def init_db(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    
    # Create products table
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                 id TEXT PRIMARY KEY,
                 name TEXT)''')
    
    # Create prices table
    c.execute('''CREATE TABLE IF NOT EXISTS prices (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 product_id TEXT,
                 source TEXT,
                 price REAL,
                 available INTEGER,
                 timestamp TEXT,
                 FOREIGN KEY(product_id) REFERENCES products(id))''')
    
    conn.commit()
    conn.close()

def import_historical_data(csv_path):
    """Import historical price data from CSV"""
    conn = sqlite3.connect('price_history.db')
    df = pd.read_csv(csv_path)
    
    # Convert columns to match database
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['available'] = df['available'].astype(int)
    
    # Insert data
    df.to_sql('prices', conn, if_exists='append', index=False)
    conn.close()
    return f"Imported {len(df)} historical records"

def save_product_data(product_id, name):
    conn = sqlite3.connect('price_history.db')
    c = conn.cursor()
    
    # Upsert product
    c.execute('''INSERT OR IGNORE INTO products (id, name) VALUES (?, ?)''', 
              (product_id, name))
    c.execute('''UPDATE products SET name = ? WHERE id = ?''', 
              (name, product_id))
    
    conn.commit()
    conn.close()

def save_price_data(product_id, source, price, available):
    conn = sqlite3.connect('price_history.db')
    c = conn.cursor()
    
    c.execute('''INSERT INTO prices 
                 (product_id, source, price, available, timestamp) 
                 VALUES (?, ?, ?, ?, ?)''',
              (product_id, source, price, int(available), 
               datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

def get_price_history(product_id):
    conn = sqlite3.connect('price_history.db')
    c = conn.cursor()
    
    c.execute('''SELECT source, price, available, timestamp 
                 FROM prices 
                 WHERE product_id = ?
                 ORDER BY timestamp DESC''', (product_id,))
    
    data = c.fetchall()
    conn.close()
    return data