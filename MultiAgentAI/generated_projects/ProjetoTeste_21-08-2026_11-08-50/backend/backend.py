from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://localhost:3306/catalogo_livros_ebooks'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret_key'

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    preco_promocional = db.Column(db.Float, nullable=False)
    quantidade_estoque = db.Column(db.Integer, nullable=False)
    formato_ebook = db.Column(db.String(100), nullable=True)
    numero_pginas = db.Column(db.Integer, nullable=True)
    idioma = db.Column(db.String(100), nullable=True)
    editora = db.Column(db.String(100), nullable=True)
    ano_publicacao = db.Column(db.Integer, nullable=True)
    avaliacao = db.Column(db.Float, nullable=True)
    quantidade Avaliacoes = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(100), nullable=False)
    dataCadastro = db.Column(db.DateTime, nullable=False)
    url_capa = db.Column(db.String(100), nullable=True)
    palavras_chave = db.Column(db.String(100), nullable=True)

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, nullable=False)
    id_produtos = db.Column(db.Integer, nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    data_pedido = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(100), nullable=False)

class Promoção(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_produtos = db.Column(db.Integer, nullable=False)
    data_inicio = db.Column(db.DateTime, nullable=False)
    data_fim = db.Column(db.DateTime, nullable=False)
    desconto = db.Column(db.Float, nullable=False)

class Avaliacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_produtos = db.Column(db.Integer, nullable=False)
    id_clientes = db.Column(db.Integer, nullable=False)
    avaliacao = db.Column(db.Float, nullable=False)
    comentario = db.Column(db.String(100), nullable=True)
    data = db.Column(db.DateTime, nullable=False)

class ProdutoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Produto
        include_fk = True

class PedidoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Pedido
        include_fk = True

class PromoçãoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Promoção
        include_fk = True

class AvaliacaoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Avaliacao
        include_fk = True

produto_schema = ProdutoSchema()
produtos_schema = ProdutoSchema(many=True)

pedido_schema = PedidoSchema()
pedidos_schema = PedidoSchema(many=True)

promoção_schema = PromoçãoSchema()
promocões_schema = PromoçãoSchema(many=True)

avaliacao_schema = AvaliacaoSchema()
avaliacoes_schema = AvaliacaoSchema(many=True)

@app.route('/produtos', methods=['GET'])
def get_produtos():
    produtos = Produto.query.all()
    return produtos_schema.jsonify(produtos)

@app.route('/produtos/<id>', methods=['GET'])
def get_produto(id):
    produto = Produto.query.get(id)
    return produto_schema.jsonify(produto)

@app.route('/pedidos', methods=['GET'])
def get_pedidos():
    pedidos = Pedido.query.all()
    return pedidos_schema.jsonify(pedidos)

@app.route('/pedidos/<id>', methods=['GET'])
def get_pedido(id):
    pedido = Pedido.query.get(id)
    return pedido_schema.jsonify(pedido)

@app.route('/promocões', methods=['GET'])
def get_promocões():
    promoções = Promoção.query.all()
    return promocões_schema.jsonify(promoções)

@app.route('/promocões/<id>', methods=['GET'])
def get_promoção(id):
    promoção = Promoção.query.get(id)
    return promoção_schema.jsonify(promoção)

@app.route('/avaliacoes', methods=['GET'])
def get_avaliacoes():
    avaliacoes = Avaliacao.query.all()
    return avaliacoes_schema.jsonify(avaliacoes)

@app.route('/avaliacoes/<id>', methods=['GET'])
def get_avaliacao(id):
    avaliacao = Avaliacao.query.get(id)
    return avaliacao_schema.jsonify(avaliacao)

@app.route('/produtos', methods=['POST'])
def criar_produto():
    produto = Produto()
    produto.titulo = request.json['titulo']
    produto.autor = request.json['autor']
    produto.categoria = request.json['categoria']
    produto.tipo = request.json['tipo']
    produto.preco = request.json['preco']
    produto.preco_promocional = request.json['preco_promocional']
    produto.quantidade_estoque = request.json['quantidade_estoque']
    produto.formato_ebook = request.json['formato_ebook']
    produto.numero_pginas = request.json['numero_pginas']
    produto.idioma = request.json['idioma']
    produto.editora = request.json['editora']
    produto.ano_publicacao = request.json['ano_publicacao']
    produto.avaliacao = request.json['avaliacao']
    produto.quantidade_Avaliacoes = request.json['quantidade_Avaliacoes']
    produto.status = request.json['status']
    produto.dataCadastro = request.json['dataCadastro']
    produto.url_capa = request.json['url_capa']
    produto.palavras_chave = request.json['palavras_chave']
    db.session.add(produto)
    db.session.commit()
    return produto_schema.jsonify(produto)

@app.route('/pedidos', methods=['POST'])
def criar_pedido():
    pedido = Pedido()
    pedido.id_cliente = request.json['id_cliente']
    pedido.id_produtos = request.json['id_produtos']
    pedido.quantidade = request.json['quantidade']
    pedido.data_pedido = request.json['data_pedido']
    pedido.status = request.json['status']
    db.session.add(pedido)
    db.session.commit()
    return pedido_schema.jsonify(pedido)

@app.route('/promocões', methods=['POST'])
def criar_promoção():
    promoção = Promoção()
    promoção.id_produtos = request.json['id_produtos']
    promoção.data_inicio = request.json['data_inicio']
    promoção.data_fim = request.json['data_fim']
    promoção.desconto = request.json['desconto']
    db.session.add(promoção)
    db.session.commit()
    return promoção_schema.jsonify(promoção)

@app.route('/avaliacoes', methods=['POST'])
def criar_avaliacao():
    avaliacao = Avaliacao()
    avaliacao.id_produtos = request.json['id_produtos']
    avaliacao.id_clientes = request.json['id_clientes']
    avaliacao.avaliacao = request.json['avaliacao']
    avaliacao.comentario = request.json['comentario']
    avaliacao.data = request.json['data']
    db.session.add(avaliacao)
    db.session.commit()
    return avaliacao_schema.jsonify(avaliacao)

if __name__ == '__main__':
    app.run(debug=True)