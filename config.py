# Web scraping configurations
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
}

# CSS Selectors (update if websites change)
SELECTORS = {
    'amazon': {
        'name': '#productTitle',
        'price': '.a-price-whole',
        'availability': '#availability'
    },
    'flipkart': {
        'name': 'span.B_NuCI',
        'price': 'div._30jeq3._16Jk6d',
        'availability': '._16FRp0'
    }
}

# Database config
DB_NAME = 'price_history.db'