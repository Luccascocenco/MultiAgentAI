from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    comentarios = db.relationship("Comentario", backref="produto")

class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(100), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey("produto.id"))

class Carrinho(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    produto_id = db.Column(db.Integer, db.ForeignKey("produto.id"))
    quantidade = db.Column(db.Integer, nullable=False)

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_hora = db.Column(db.DateTime, nullable=False)
    total = db.Column(db.Float, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))

login_manager = LoginManager(app)
@login_manager.user_loader
def load_user(id):
    return User.query.get(id)

@app.route("/login", methods=["POST"])
def login():
    username = request.json["username"]
    password = request.json["password"]
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        return jsonify({"message": "Login realizado com sucesso!"})
    return jsonify({"message": "Login falhou!"})

@app.route("/register", methods=["POST"])
def register():
    username = request.json["username"]
    password = request.json["password"]
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({"message": "Já existe um usuário com esse nome de usuário!"})
    user = User(username=username, password=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Usuário criado com sucesso!"})

@app.route("/produto", methods=["POST"])
@login_required
def produto():
    nome = request.json["nome"]
    preco = request.json["preco"]
    produto = Produto(nome=nome, preco=preco)
    db.session.add(produto)
    db.session.commit()
    return jsonify({"message": "Produto criado com sucesso!"})

@app.route("/carrinho", methods=["POST"])
@login_required
def carrinho():
    produto_id = request.json["produto_id"]
    quantidade = request.json["quantidade"]
    carrinho = Carrinho(usuario_id=id(), produto_id=produto_id, quantidade=quantidade)
    db.session.add(carrinho)
    db.session.commit()
    return jsonify({"message": "Carrinho criado com sucesso!"})

@app.route("/pedido", methods=["POST"])
@login_required
def pedido():
    data_hora = request.json["data_hora"]
    total = request.json["total"]
    pedido = Pedido(data_hora=data_hora, total=total, usuario_id=id())
    db.session.add(pedido)
    db.session.commit()
    return jsonify({"message": "Pedido criado com sucesso!"})

if __name__ == "__main__":
    app.run(debug=True)