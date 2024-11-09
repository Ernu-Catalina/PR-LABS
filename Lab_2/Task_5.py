from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup
import re
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

# Initialize the database
db = SQLAlchemy(app)

# Ensure the upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


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


# Initialize the database
with app.app_context():
    db.create_all()


# File upload route
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"message": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    if file.filename.endswith('.json'):
        try:
            with open(file_path, 'r') as f:
                file_data = json.load(f)
            return jsonify({"message": "File uploaded successfully", "data": file_data}), 200
        except json.JSONDecodeError:
            return jsonify({"message": "Uploaded file is not valid JSON"}), 400
    else:
        return jsonify({"message": "File uploaded successfully"}), 200


# CRUD Operations with Pagination

@app.route('/products', methods=['GET'])
def get_products():
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 5))
    products = Product.query.offset(offset).limit(limit).all()
    return jsonify([{
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "old_price": p.old_price,
        "new_price": p.new_price,
        "created_at": p.created_at
    } for p in products])


@app.route('/product', methods=['POST'])
def create_product():
    data = request.json
    new_product = Product(
        name=data['name'],
        description=data['description'],
        old_price=data.get('old_price'),
        new_price=data['new_price']
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "Product created successfully"}), 201


@app.route('/product', methods=['PUT'])
def update_product():
    product_id = request.args.get('id')
    product = Product.query.get(product_id)

    if not product:
        return jsonify({"message": "Product not found"}), 404

    data = request.json
    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.old_price = data.get('old_price', product.old_price)
    product.new_price = data.get('new_price', product.new_price)

    db.session.commit()
    return jsonify({"message": "Product updated successfully"}), 200


@app.route('/product', methods=['DELETE'])
def delete_product():
    product_id = request.args.get('id')
    product = Product.query.get(product_id)

    if not product:
        return jsonify({"message": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully"}), 200


if __name__ == '__main__':
    app.run(debug=True)
