import csv
import requests
import time
import config
import sys

BASE_URL = config.SHOP_URL + f"/webapi/front/{config.SHOP_LANG}/products/{config.SHOP_CURRENCY}/" + "{}"
print(f"Selected Shoper URL: {BASE_URL}")

global count404
count404 = 0

def fetch_product_data(product_id):
    global count404
    if count404 == 5:
        print("Too many 404, range probably invalid. Further actions could result in IP block")
        sys.exit()
    url = BASE_URL.format(product_id)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        count404 +=1
        return None
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
                rows.append([
                    product_id,
                    product_name,
                    option_id,
                    option_name,
                    value.get("id"),
                    value.get("name"),
                    value.get("order")
                ])
    print(f"Parsed product id {product_id}")
    print(rows)
    return rows

def main():
    with open(config.OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["product_id", "product_name", "option_id", "option_name", "value_id", "value_name", "value_order"])
        
        for product_id in config.PRODUCT_IDS:
            product_data = fetch_product_data(product_id)
            if product_data:
                rows = parse_product_data(product_data)
                writer.writerows(rows)
            time.sleep(config.CRAWL_DELAY)
    
    print(f"File saved: {config.OUTPUT_FILE}")

if __name__ == "__main__":
    main()