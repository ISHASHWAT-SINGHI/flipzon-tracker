# Add to imports
import matplotlib.pyplot as plt
import os
import sys
from datetime import datetime

# Add after logging setup
def generate_run_report(products):
    """Create visual report for each run"""
    conn = sqlite3.connect('price_history.db')
    report = {"timestamp": datetime.now().isoformat(), "products": []}
    
    for product in products:
        product_id = product['id']
        df = pd.read_sql_query(f"""
            SELECT timestamp, price, source 
            FROM prices 
            WHERE product_id = '{product_id}'
            ORDER BY timestamp DESC
            LIMIT 30
        """, conn)
        
        if not df.empty:
            # Generate plot
            plt.figure(figsize=(10, 6))
            for source in df['source'].unique():
                source_df = df[df['source'] == source]
                plt.plot(source_df['timestamp'], source_df['price'], 'o-', label=source)
            
            plt.title(f"{product['name']} Price Trend")
            plt.xlabel('Date')
            plt.ylabel('Price (₹)')
            plt.xticks(rotation=45)
            plt.legend()
            plt.tight_layout()
            plot_path = f"reports/{product_id}_trend.png"
            os.makedirs("reports", exist_ok=True)
            plt.savefig(plot_path)
            plt.close()
            
            # Add to report
            report["products"].append({
                "id": product_id,
                "name": product['name'],
                "latest_price": df.iloc[0]['price'],
                "plot_path": plot_path
            })
    
    # Save JSON report
    with open("reports/latest_run.json", "w") as f:
        json.dump(report, f, indent=2)
    
    return report

# Modify main execution
if __name__ == "__main__":
    try:
        init_db('price_history.db')
        products = load_products()
        scrape_job()
        report = generate_run_report(products)
        logging.info(f"Run completed. Report: {report}")
    except Exception as e:
        logging.exception("Critical error in main execution")
        sys.exit(1)