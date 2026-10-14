from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bluebeauty.db"
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)

class Benefit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

@app.route("/products", methods=["GET"])
def get_products():
    products = Product.query.all()
    return jsonify([{"id": p.id, "name": p.name, "image": p.image, "description": p.description, "price": p.price} for p in products])

@app.route("/benefits", methods=["GET"])
def get_benefits():
    benefits = Benefit.query.all()
    return jsonify([{"id": b.id, "name": b.name, "description": b.description} for b in benefits])

@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([{"id": u.id, "name": u.name, "email": u.email} for u in users])

@app.route("/add_product", methods=["POST"])
def add_product():
    data = request.get_json()
    product = Product(name=data["name"], image=data["image"], description=data["description"], price=data["price"])
    db.session.add(product)
    db.session.commit()
    return jsonify({"message": "Product added successfully"})

@app.route("/add_benefit", methods=["POST"])
def add_benefit():
    data = request.get_json()
    benefit = Benefit(name=data["name"], description=data["description"])
    db.session.add(benefit)
    db.session.commit()
    return jsonify({"message": "Benefit added successfully"})

@app.route("/add_user", methods=["POST"])
def add_user():
    data = request.get_json()
    user = User(name=data["name"], email=data["email"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User added successfully"})

if __name__ == "__main__":
    app.run(debug=True)