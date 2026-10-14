from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Define models
class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    preco_promocional = db.Column(db.Float, nullable=False)
    quantidade_estoque = db.Column(db.Integer, nullable=False)
    formato_ebook = db.Column(db.String(100), nullable=False)
    numero_pginas = db.Column(db.Integer, nullable=False)
    idioma = db.Column(db.String(100), nullable=False)
    editora = db.Column(db.String(100), nullable=False)
    ano_publicacao = db.Column(db.Integer, nullable=False)
    avaliacao = db.Column(db.Float, nullable=False)
    quantidade_avalies = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(100), nullable=False)
    data_cadastro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    url_capa = db.Column(db.String(100), nullable=False)
    palavras_chave = db.Column(db.String(100), nullable=False)

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, nullable=False)
    id_produto = db.Column(db.Integer, nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    data_pedido = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(100), nullable=False)

class Promoção(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_produto = db.Column(db.Integer, nullable=False)
    data_inicio = db.Column(db.DateTime, nullable=False)
    data_fim = db.Column(db.DateTime, nullable=False)
    desconto = db.Column(db.Float, nullable=False)

class Avaliação(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_produto = db.Column(db.Integer, nullable=False)
    id_cliente = db.Column(db.Integer, nullable=False)
    avaliacao = db.Column(db.Float, nullable=False)
    comentario = db.Column(db.String(100), nullable=False)
    data = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

# Define schemas
class ProdutoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Produto
        load_instance = True

class PedidoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Pedido
        load_instance = True

class PromoçãoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Promoção
        load_instance = True

class AvaliaçãoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Avaliação
        load_instance = True

class ClienteSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Cliente
        load_instance = True

# Define routes
@app.route('/produtos', methods=['GET'])
def get_produtos():
    produtos = Produto.query.all()
    return ProdutoSchema(many=True).jsonify(produtos)

@app.route('/produtos/<int:id>', methods=['GET'])
def get_produto(id):
    produto = Produto.query.get(id)
    return ProdutoSchema().jsonify(produto)

@app.route('/produtos', methods=['POST'])
def criar_produto():
    produto = Produto(
        titulo=request.json['titulo'],
        autor=request.json['autor'],
        categoria=request.json['categoria'],
        tipo=request.json['tipo'],
        preco=request.json['preco'],
        preco_promocional=request.json['preco_promocional'],
        quantidade_estoque=request.json['quantidade_estoque'],
        formato_ebook=request.json['formato_ebook'],
        numero_pginas=request.json['numero_pginas'],
        idioma=request.json['idioma'],
        editora=request.json['editora'],
        ano_publicacao=request.json['ano_publicacao'],
        avaliacao=request.json['avaliacao'],
        quantidade_avalies=request.json['quantidade_avalies'],
        status=request.json['status'],
        url_capa=request.json['url_capa'],
        palavras_chave=request.json['palavras_chave']
    )
    db.session.add(produto)
    db.session.commit()
    return ProdutoSchema().jsonify(produto)

@app.route('/pedidos', methods=['GET'])
def get_pedidos():
    pedidos = Pedido.query.all()
    return PedidoSchema(many=True).jsonify(pedidos)

@app.route('/pedidos/<int:id>', methods=['GET'])
def get_pedido(id):
    pedido = Pedido.query.get(id)
    return PedidoSchema().jsonify(pedido)

@app.route('/pedidos', methods=['POST'])
def criar_pedido():
    pedido = Pedido(
        id_cliente=request.json['id_cliente'],
        id_produto=request.json['id_produto'],
        quantidade=request.json['quantidade'],
        data_pedido=request.json['data_pedido'],
        status=request.json['status']
    )
    db.session.add(pedido)
    db.session.commit()
    return PedidoSchema().jsonify(pedido)

@app.route('/promocoes', methods=['GET'])
def get_promocoes():
    promocoes = Promoção.query.all()
    return PromoçãoSchema(many=True).jsonify(promocoes)

@app.route('/promocoes/<int:id>', methods=['GET'])
def get_promocao(id):
    promocao = Promoção.query.get(id)
    return PromoçãoSchema().jsonify(promocao)

@app.route('/promocoes', methods=['POST'])
def criar_promocao():
    promocao = Promoção(
        id_produto=request.json['id_produto'],
        data_inicio=request.json['data_inicio'],
        data_fim=request.json['data_fim'],
        desconto=request.json['desconto']
    )
    db.session.add(promocao)
    db.session.commit()
    return PromoçãoSchema().jsonify(promocao)

@app.route('/avaliacoes', methods=['GET'])
def get_avaliacoes():
    avaliacoes = Avaliação.query.all()
    return AvaliaçãoSchema(many=True).jsonify(avaliacoes)

@app.route('/avaliacoes/<int:id>', methods=['GET'])
def get_avaliacao(id):
    avaliacao = Avaliação.query.get(id)
    return AvaliaçãoSchema().jsonify(avaliacao)

@app.route('/avaliacoes', methods=['POST'])
def criar_avaliacao():
    avaliacao = Avaliação(
        id_produto=request.json['id_produto'],
        id_cliente=request.json['id_cliente'],
        avaliacao=request.json['avaliacao'],
        comentario=request.json['comentario'],
        data=request.json['data']
    )
    db.session.add(avaliacao)
    db.session.commit()
    return AvaliaçãoSchema().jsonify(avaliacao)

if __name__ == '__main__':
    app.run(debug=True)