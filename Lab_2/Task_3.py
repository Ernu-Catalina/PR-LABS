from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Product Model
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


with app.app_context():
    db.create_all()


def get_product_by_identifier(identifier):
    if identifier.isdigit():
        return Product.query.get(int(identifier))
    return Product.query.filter_by(name=identifier).first()


@app.route('/product', methods=['POST'])
def create_product():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', "N/A")
    old_price = data.get('old_price')
    new_price = data.get('new_price')

    if not name or not new_price:
        return jsonify({"error": "Name and new_price are required"}), 400

    if Product.query.filter_by(name=name).first():
        return jsonify({"error": "Product already exists"}), 409

    new_product = Product(name=name, description=description, old_price=old_price, new_price=new_price)
    db.session.add(new_product)
    db.session.commit()

    return jsonify({"message": f"Product '{name}' created successfully."}), 201


@app.route('/product', methods=['GET'])
def read_product():
    identifier = request.args.get('id_or_name')
    if not identifier:
        return jsonify({"error": "Please provide an 'id_or_name' query parameter"}), 400

    product = get_product_by_identifier(identifier)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    return jsonify({
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "old_price": product.old_price,
        "new_price": product.new_price,
        "created_at": product.created_at
    })


@app.route('/product', methods=['PUT'])
def update_product():
    identifier = request.args.get('id_or_name')
    if not identifier:
        return jsonify({"error": "Please provide an 'id_or_name' query parameter"}), 400

    product = get_product_by_identifier(identifier)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json()
    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.old_price = data.get('old_price', product.old_price)
    product.new_price = data.get('new_price', product.new_price)

    db.session.commit()

    return jsonify({"message": f"Product '{product.name}' updated successfully."})


@app.route('/product', methods=['DELETE'])
def delete_product():
    identifier = request.args.get('id_or_name')
    if not identifier:
        return jsonify({"error": "Please provide an 'id_or_name' query parameter"}), 400

    product = get_product_by_identifier(identifier)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()

    return jsonify({"message": f"Product '{product.name}' deleted successfully."})


if __name__ == '__main__':
    app.run(debug=True)
