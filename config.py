# config.py
import os
SHOP_URL = "https://123456.shoparena.pl" #Example: https://123456.shoparena.pl
SHOP_LANG = "pl_PLN" #Example: "pl_PL", "en_US", "nl_NL"
SHOP_CURRENCY = "PLN" #Example: "PLN", "EUR"
#SHOP_API_VERSION = "1.4.0" #Example: ShoperSaaS: "1.4.0"; mijndomein: "1.2.0"

EXPORT_TYPE = 1 #1-standard 2-mijndomein-style

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, "products.csv")

CRAWL_DELAY = 1 #crawl delay, 1 request per second is safe for Shoper