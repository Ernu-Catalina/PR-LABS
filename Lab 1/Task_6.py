import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from functools import reduce

MDL_TO_EUR = 0.052
EUR_TO_MDL = 1 / MDL_TO_EUR


def validate_price(price_str):
    clean_price = re.sub(r'[^\d]', '', price_str)
    if clean_price.isdigit():
        return int(clean_price) // 100
    return None


def convert_price_to_eur(product):
    if product['currency'] == 'MDL':
        product['price_in_eur'] = round(product['price'] * MDL_TO_EUR, 2)  # Convert MDL to EUR
    elif product['currency'] == 'EUR':
        product['price_in_mdl'] = round(product['price'] * EUR_TO_MDL, 2)  # Convert EUR to MDL
    return product


def extract_products(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        products = soup.find_all(class_='product-details')

        product_list = []

        for product in products:
            name_tag = product.find(class_='name')
            price_tag = product.find(class_='price')
            link_tag = name_tag.find('a') if name_tag else None

            product_name = name_tag.get_text(strip=True) if name_tag else "N/A"
            product_name = product_name.strip()

            price_text = price_tag.get_text(strip=True) if price_tag else "N/A"
            price_text_cleaned = re.sub(r'Ex Tax:.*', '', price_text)  # Remove "Ex Tax" and everything after it
            price_text_cleaned = price_text_cleaned.replace('Lei', '').strip()

            price = validate_price(price_text_cleaned.split()[0])
            discounted_price = None

            if len(price_text_cleaned.split()) > 1:
                discounted_price = validate_price(price_text_cleaned.split()[1])

            product_list.append({
                'name': product_name,
                'price': price,
                'discounted_price': discounted_price,
                'currency': 'MDL'
            })

        return product_list
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return []


def map_prices_to_eur(product):
    product = convert_price_to_eur(product)
    if product['discounted_price']:
        product['discounted_price_in_eur'] = round(product['discounted_price'] * MDL_TO_EUR, 2)
    return product


def filter_products_by_price_range(product, min_price=5, max_price=50):
    return min_price <= product['price_in_eur'] <= max_price


def sum_prices(total, product):
    return total + product['price_in_eur']


def process_products(url):
    products = extract_products(url)

    mapped_products = list(map(map_prices_to_eur, products))

    filtered_products = list(filter(lambda p: filter_products_by_price_range(p, 5, 50), mapped_products))

    total_price_sum = reduce(sum_prices, filtered_products, 0)

    final_data = {
        'filtered_products': filtered_products,
        'total_price_sum_in_eur': total_price_sum,
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    }

    print(f"Processed on: {final_data['timestamp']}")
    print(f"Total Price Sum (EUR): {final_data['total_price_sum_in_eur']} EUR")
    print("Filtered Products:\n")
    for product in final_data['filtered_products']:
        print(f"Product Name: {product['name']}")
        print(f"Price: {product['price']} MDL / {product['price_in_eur']} EUR")
        if product['discounted_price']:
            print(f"Discounted Price: {product['discounted_price']} MDL / {product['discounted_price_in_eur']} EUR")
        print('---')



url = "https://educationalcentre.md/shop/index.php?route=product/category&path=2350_2355_2361"
process_products(url)
