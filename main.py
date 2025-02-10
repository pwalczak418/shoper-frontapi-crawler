#v0.04

import csv
import requests
import time
import config
import sys

print(f"Selected Shop URL: {config.SHOP_URL}")
BASE_URL = config.SHOP_URL + f"/webapi/front/{config.SHOP_LANG}/products/{config.SHOP_CURRENCY}/" + "{}"
PRODUCT_LIST_URL = config.SHOP_URL + f"/webapi/front/{config.SHOP_LANG}/products/{config.SHOP_CURRENCY}/list?page=" + "{}" + "&limit=50"
OPTION_URL = config.SHOP_URL + f"/webapi/front/{config.SHOP_LANG}/products/{config.SHOP_CURRENCY}/" + "{}" + "/stock/"

session = requests.Session()
session.headers.update({
    'User-Agent': 'shoper-frontapi-crawler /0.04 (+https://github.com/pwalczak418/shoper-frontapi-crawler)',
    "Content-Type": "application/json",
})

###Export type 1

def fetch_product_data(product_id):
    url = BASE_URL.format(product_id)
    response = session.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def parse_product_data(product_data):
    rows = []
    product_id = product_data.get("id")
    product_name = product_data.get("name", "")

    options = product_data.get("options_configuration", [])
    for option in options:
        if "stock" not in option or not option.get("stock"):
            option_id = option.get("id")
            option_name = option.get("name", "")
            for value in option.get("values", []):
                value_id = value.get("id")
                rows.append([
                    product_id,
                    product_name,
                    option_id,
                    option_name,
                    value_id,
                    value.get("name"),
                    value.get("order"),
                    get_option_price(product_id, option_id, value_id)
                ])
                time.sleep(config.CRAWL_DELAY)
    print(f"Parsed product id {product_id}")
    print(rows)
    return rows

def get_products_ids():
    defaultpage = 1
    products_ids = []
    url = PRODUCT_LIST_URL.format(defaultpage)
    response = session.get(url)
    data = response.json()
    pages = data["pages"]

    for page in range(1, pages + 1):
        print(f"Scanning products info, page {page} of {pages}")
        url = PRODUCT_LIST_URL.format(page)
        response = session.get(url)
        data = response.json()
        products_ids.extend([product["id"] for product in data["list"]])
        time.sleep(config.CRAWL_DELAY)
    
    return products_ids

def get_option_price(product_id, option_id, value_id):
    url = OPTION_URL.format(product_id)
    postdata = {
    "options": {
        str(option_id): value_id
        }
    }
    response = session.post(url, json=postdata)
    received_data = response.json()
    price_float = received_data["price"]["gross"]["base_float"]
    return price_float

###Export type 2

def parse_product_data_type2(product_data):
    rows = []
    product_id = product_data.get("id")
    product_code = product_data.get("code")
    product_name = product_data.get("name", "")
    stock_id = "" #This only apply for stock variants
    option_code = "" #This only apply for stock variants

    producer_data = product_data.get("producer", {})
    producer = producer_data.get("name", "")

    activity = "1" #FrontAPI doesn't operate on non-active products
    option_ean = "" #This only apply for stock variants

    option_avail_data = product_data.get("availability", {})
    option_avail = option_avail_data.get("name")

    option_weight_data = product_data.get("weight", {})
    option_weight = option_weight_data.get("weight_float", "0")

    option_time = "" #FrontAPI doesn't provide that data
    avail_type = "" #FrontAPI doesn't provide that data
    sold = "" #FrontAPI doesn't provide that data
    option_images = ""
    price_type = "1" #Pricetype from frontAPI is always 1

    options = product_data.get("options_configuration", [])
    for option in options:
        if "stock" not in option or not option.get("stock"):
            option_get_name = option.get("name", "")
            option_id = option.get("id")
            for value in option.get("values", []):
                value_id = value.get("id")
                value_name = value.get("name")
                option_name = f"['{value_name}']"
                rows.append([
                    product_id, #id_prod
                    product_code, #code_prod
                    product_name, #name_prod
                    option_name, #option_prod - only 1 option
                    stock_id, #option_id
                    option_code, #option_code
                    producer, #producer
                    activity, #activity
                    option_ean, #option_ean
                    get_option_price(product_id, option_id, value_id), #option_price
                    option_avail, #option_avail
                    option_weight, #option_weight
                    option_time, #option_time
                    option_avail, #avail_type
                    sold, #sold
                    option_images,
                    price_type
                ])
                time.sleep(config.CRAWL_DELAY)
    print(f"Parsed product id {product_id}")
    print(rows)
    return rows

###Main Function

def main():

    if config.EXPORT_TYPE == 1:
        print("Selected Export type 1")
        products_ids = get_products_ids()
        with open(config.OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["product_id", "product_name", "option_id", "option_name", "value_id", "value_name", "value_order", "option_float_price"])
            
            for product_id in products_ids:
                product_data = fetch_product_data(product_id)
                if product_data:
                    rows = parse_product_data(product_data)
                    writer.writerows(rows)
                time.sleep(config.CRAWL_DELAY)
        
        print(f"File saved: {config.OUTPUT_FILE}")
    
    elif config.EXPORT_TYPE == 2:
        print("Selected Export type 2")
        products_ids = get_products_ids()
        with open(config.OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["id_prod", "code_prod", "name_prod", "option_prod", "option_id", "option_code", "producer", "activity", "option_ean", "option_price", "option_avail", "option_weight", "option_time", "avail_type", "sold", "option_images", "pricetype"])            
            for product_id in products_ids:
                product_data = fetch_product_data(product_id)
                if product_data:
                    rows = parse_product_data_type2(product_data)
                    writer.writerows(rows)
                time.sleep(config.CRAWL_DELAY)
        
        print(f"File saved: {config.OUTPUT_FILE}")


    else:
        print("You need to choose the type of export")

if __name__ == "__main__":
    main()