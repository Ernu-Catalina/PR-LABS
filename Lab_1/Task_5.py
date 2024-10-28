import requests
from bs4 import BeautifulSoup
import re


def extract_additional_data(product_url):
    """Extract additional data from the product URL."""
    response = requests.get(product_url)
    if response.status_code == 200:
        product_soup = BeautifulSoup(response.content, 'html.parser')
        description_tag = product_soup.find(class_='description')
        product_description = description_tag.get_text(strip=True) if description_tag else "N/A"
        return product_description
    else:
        print(f"Failed to retrieve the product page. Status code: {response.status_code}")
        return "N/A"

    1
def validate_price(price_str):
    """Validate price and ensure it is an integer after removing the last two zeros."""
    # Remove 'Lei' and any other non-numeric characters
    clean_price = re.sub(r'[^\d]', '', price_str)
    if clean_price.isdigit():
        return int(clean_price) // 100  # Divide by 100 to remove the last two zeros
    return None


def extract_products(url):
    """Extract product information from the given URL."""
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        products = soup.find_all(class_='product-details')

        product_list = []

        for product in products:
            name_tag = product.find(class_='name')
            price_tag = product.find(class_='price')
            link_tag = name_tag.find('a') if name_tag else None

            # Extract and trim product name
            product_name = name_tag.get_text(strip=True) if name_tag else "N/A"
            product_name = product_name.strip()  # Trim leading/trailing spaces

            # Extract price and clean it
            price_text = price_tag.get_text(strip=True) if price_tag else "N/A"
            price_text_cleaned = re.sub(r'Ex Tax:.*', '', price_text)  # Remove "Ex Tax" and everything after it
            price_text_cleaned = price_text_cleaned.replace('Lei', '').strip()  # Remove currency and trim spaces

            # Validate and convert prices
            price = validate_price(price_text_cleaned.split()[0])  # Get the main price
            discounted_price = None  # Default to None for no discounted price

            # Check for additional price information (i.e., if a discounted price exists)
            if len(price_text_cleaned.split()) > 1:
                discounted_price = validate_price(price_text_cleaned.split()[1])  # Get the discounted price

            # Extract the product link
            product_link = link_tag['href'] if link_tag else "N/A"

            # Extract additional data from the product link
            additional_data = extract_additional_data(product_link)

            # Store product details in the list
            product_list.append({
                'name': product_name,
                'price': price,
                'discounted_price': discounted_price,
                'link': product_link,
                'description': additional_data.strip()  # Trim whitespaces in description
            })

        # Print the extracted product details
        for product in product_list:
            print(f"Product Name: {product['name']}")
            print(f"Price: {product['price']} Lei")
            if product['discounted_price'] is not None:
                print(f"Discounted Price: {product['discounted_price']} Lei")
            print(f"Product Link: {product['link']}")
            print(f"Description: {product['description']}")
            print('---')

    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")


# Replace with the URL of the page you want to scrape
url = "https://educationalcentre.md/shop/index.php?route=product/category&path=2350_2355_2361"
extract_products(url)
