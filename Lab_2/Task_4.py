from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify
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
            price_text_cleaned = re.sub(r'Ex Tax:.*', '', price_text).replace('Lei', '').strip()
            price = validate_price(price_text_cleaned.split()[0])
            discounted_price = validate_price(price_text_cleaned.split()[1]) if len(price_text_cleaned.split()) > 1 else None
            product_link = link_tag['href'] if link_tag else "N/A"
            additional_data = extract_additional_data(product_link)

            product_list.append({
                'name': product_name,
                'price': price,
                'discounted_price': discounted_price,
                'link': product_link,
                'description': additional_data.strip()
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

# CRUD Endpoints
@app.route('/product', methods=['POST'])
def create_product():
    data = request.get_json()
    new_product = Product(
        name=data['name'],
        description=data['description'],
        old_price=data.get('old_price'),
        new_price=data['new_price']
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "Product created", "product": data}), 201

@app.route('/product', methods=['GET'])
def get_product():
    id_or_name = request.args.get('id_or_name')
    product = Product.query.filter(
        (Product.id == id_or_name) | (Product.name == id_or_name)
    ).first()
    if product:
        return jsonify({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'old_price': product.old_price,
            'new_price': product.new_price,
            'created_at': product.created_at
        })
    return jsonify({"message": "Product not found"}), 404

@app.route('/products', methods=['GET'])
def get_products():
    offset = request.args.get('offset', default=0, type=int)
    limit = request.args.get('limit', default=5, type=int)
    products = Product.query.offset(offset).limit(limit).all()
    total_products = Product.query.count()
    product_list = [{
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'old_price': product.old_price,
        'new_price': product.new_price,
        'created_at': product.created_at
    } for product in products]
    return jsonify({
        'products': product_list,
        'total': total_products,
        'offset': offset,
        'limit': limit,
        'has_more': offset + limit < total_products
    })

@app.route('/product', methods=['PUT'])
def update_product():
    id_or_name = request.args.get('id_or_name')
    data = request.get_json()
    product = Product.query.filter(
        (Product.id == id_or_name) | (Product.name == id_or_name)
    ).first()
    if product:
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.old_price = data.get('old_price', product.old_price)
        product.new_price = data.get('new_price', product.new_price)
        db.session.commit()
        return jsonify({"message": "Product updated"})
    return jsonify({"message": "Product not found"}), 404

@app.route('/product', methods=['DELETE'])
def delete_product():
    id_or_name = request.args.get('id_or_name')
    product = Product.query.filter(
        (Product.id == id_or_name) | (Product.name == id_or_name)
    ).first()
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted"})
    return jsonify({"message": "Product not found"}), 404

# Main script for testing
url = "https://educationalcentre.md/shop/index.php?route=product/category&path=2350_2355_2361"

if __name__ == '__main__':
    with app.app_context():
        products = extract_products(url)
        add_products_to_db(products)
        print("Products have been added to the database.")
    app.run(debug=True)
