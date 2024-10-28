from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re

db = SQLAlchemy()


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    old_price = db.Column(db.Float, nullable=True)
    new_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Product {self.name}>"


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()


def extract_additional_data(product_url):
    response = requests.get(product_url)
    if response.status_code == 200:
        product_soup = BeautifulSoup(response.content, 'html.parser')
        description_tag = product_soup.find(class_='description')
        product_description = description_tag.get_text(strip=True) if description_tag else "N/A"
        return product_description
    else:
        print(f"Failed to retrieve the product page. Status code: {response.status_code}")
        return "N/A"


def validate_price(price_str):
    clean_price = re.sub(r'[^\d]', '', price_str)
    if clean_price.isdigit():
        return int(clean_price) // 100
    return None


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

            price_text = price_tag.get_text(strip=True) if price_tag else "N/A"
            price_text_cleaned = re.sub(r'Ex Tax:.*', '', price_text)
            price_text_cleaned = price_text_cleaned.replace('Lei', '').strip()

            price = validate_price(price_text_cleaned.split()[0])
            discounted_price = None

            if len(price_text_cleaned.split()) > 1:
                discounted_price = validate_price(price_text_cleaned.split()[1])

            product_link = link_tag['href'] if link_tag else "N/A"

            additional_data = extract_additional_data(product_link)

            product_list.append({
                'name': product_name,
                'price': price,
                'discounted_price': discounted_price,
                'link': product_link,
                'description': additional_data.strip()  # Trim whitespaces in description
            })

        return product_list

    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return []


def add_products_to_db(products):
    for product in products:
        existing_product = Product.query.filter_by(name=product['name']).first()

        if existing_product:
            print(f"Product '{product['name']}' already exists. Skipping...")
            continue

        new_product = Product(
            name=product['name'],
            description=product['description'],
            old_price=product['discounted_price'],
            new_price=product['price']
        )

        db.session.add(new_product)
    db.session.commit()


url = "https://educationalcentre.md/shop/index.php?route=product/category&path=2350_2355_2361"

if __name__ == '__main__':
    with app.app_context():
        products = extract_products(url)
        add_products_to_db(products)
        print("Products have been added to the database.")
