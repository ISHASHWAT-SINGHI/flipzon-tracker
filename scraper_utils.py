import requests
from requests.exceptions import Timeout
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from config import HEADERS, SELECTORS
import time

def get_dynamic_page(url):
    """Handle JavaScript-rendered pages"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument(f'user-agent={HEADERS["User-Agent"]}')
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    try:
        driver.get(url)
        time.sleep(3)  # Allow page to render
        return driver.page_source
    finally:
        driver.quit()

def scrape_product(url):
    # Modify scrape_product function
    def scrape_product(url, timeout=15):
        site = 'amazon' if 'amazon' in url else 'flipkart'
        result = {
            'name': "Unknown Product",
            'price': 0.0,
            'available': False,
            'success': False
        }

        try:
            # First try static scraping with timeout
            response = requests.get(url, headers=HEADERS, timeout=timeout)
            response.raise_for_status()
            source = response.text
            result['method'] = 'static'
        except (Timeout, Exception):
            try:
                # Fallback to dynamic rendering with timeout
                source = get_dynamic_page(url, timeout)
                result['method'] = 'dynamic'
            except Exception as e:
                logging.error(f"Scrape failed for {url}: {str(e)}")
                return result
    
    soup = BeautifulSoup(source, 'html.parser')
    selectors = SELECTORS[site]
    
    # Extract data
    name_tag = soup.select_one(selectors['name'])
    price_tag = soup.select_one(selectors['price'])
    avail_tag = soup.select_one(selectors['availability'])
    
    # Handle missing data
    name = name_tag.get_text(strip=True) if name_tag else "Unknown Product"
    price = float(price_tag.get_text(strip=True).replace(',', '')) if price_tag else 0.0
    available = not bool(avail_tag) if avail_tag else True
    
    return {
        'name': name,
        'price': price,
        'available': available,
        'success': bool(price_tag)  # Flag for successful scrape
    }
# Update get_dynamic_page
def get_dynamic_page(url, timeout=30):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument(f'user-agent={HEADERS["User-Agent"]}')
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    try:
        driver.set_page_load_timeout(timeout)
        driver.get(url)
        time.sleep(2)  # Allow initial render
        return driver.page_source
    except TimeoutException:
        logging.warning(f"Page load timed out for {url}")
        return driver.page_source  # Return partial content
    finally:
        driver.quit()