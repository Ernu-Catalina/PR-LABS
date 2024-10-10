import requests
from bs4 import BeautifulSoup
import re


def extract_products(url):
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all product grid items
        products = soup.find_all(class_='product-details')

        # Initialize a list to hold product details
        product_list = []

        # Loop through each product item and extract details
        for product in products:
            name_tag = product.find(class_='name')
            price_tag = product.find(class_='price')

            # Extract the product name
            product_name = name_tag.get_text(strip=True) if name_tag else "N/A"

            # Extract price text and clean it
            price_text = price_tag.get_text(strip=True) if price_tag else "N/A"
            price_text_cleaned = re.sub(r'Ex Tax:.*', '', price_text)  # Remove "Ex Tax" and everything after it
            price_text_cleaned = price_text_cleaned.replace('Lei', '').strip()  # Remove currency and trim spaces

            # Determine if the price is discounted
            prices = price_text_cleaned.split()  # Split by whitespace
            price = f"{prices[0]} Lei" if len(prices) > 0 else "N/A"
            discounted_price = "N/A"  # Default to "N/A"

            # Check for additional price information (indicative of discounts)
            if len(prices) > 1:
                discounted_price = f"{prices[1]} Lei"  # Capture discounted price

            # Append the product details to the list
            product_list.append({
                'name': product_name,
                'price': price,
                'discounted_price': discounted_price if discounted_price != "N/A" else "N/A"
            })

        # Print the extracted product details
        for product in product_list:
            print(f"Product Name: {product['name']}")
            print(f"Price: {product['price']}")
            if product['discounted_price'] != "N/A":
                print(f"Discounted Price: {product['discounted_price']}")
            print('---')

    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")


url = "https://educationalcentre.md/shop/index.php?route=product/category&path=2350_2355_2361"
extract_products(url)
