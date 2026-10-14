from flask import Flask
import mysql.connector
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Conexão com o banco de dados
db = SQLAlchemy(app)
db.connect()

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user:password@localhost/db'

# Definição das tabelas do banco de dados
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    payment_method = db.Column(db.String(100), nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False)

# Definição das rotas
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return {'users': [user.name for user in users]}

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return {'products': [product.name for product in products]}

@app.route('/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    return {'orders': [order.user_id for order in orders]}

@app.route('/payments', methods=['GET'])
def get_payments():
    payments = Payment.query.all()
    return {'payments': [payment.order_id for payment in payments]}

if __name__ == '__main__':
    app.run(debug=True)