from flask import Flask, jsonify, request
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")

app = Flask(__name__, static_folder="static", static_url_path="")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_banco():
    # Cria o banco a partir do schema.sql, só na primeira vez
    if os.path.exists(DB_PATH) and os.path.getsize(DB_PATH) > 0:
        return

    conn = get_db_connection()
    with open(SCHEMA_PATH, encoding="utf-8") as arquivo:
        conn.executescript(arquivo.read())
    conn.commit()
    conn.close()

@app.route("/", methods=["GET"])
def home():
    return app.send_static_file("index.html")

@app.route("/api/produtos", methods=["GET"])
def listar_produtos():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, nome, descricao, preco, avaliacao_produto FROM produtos").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])

@app.route("/api/produtos/<int:item_id>", methods=["GET"])
def obter_produto(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id, nome, descricao, preco, avaliacao_produto FROM produtos WHERE id = ?",
        (item_id,)
    ).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Produto não encontrado"}), 404
    return jsonify(dict(linha))

@app.route("/api/produtos", methods=["POST"])
def criar_produto():
    dados = request.get_json()
    conn = get_db_connection()
    conn.execute("INSERT INTO produtos (nome, descricao, preco, avaliacao_produto) VALUES (?, ?, ?, ?)",
                 (dados["nome"], dados.get("descricao"), dados["preco"], dados.get("avaliacao_produto")))
    conn.commit()
    novo_id = conn.lastrowid
    conn.close()
    return jsonify({"id": novo_id}), 201

@app.route("/api/pedidos", methods=["GET"])
def listar_pedidos():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, id_produto, quantidade, subtotal, data_pedido FROM pedidos").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])

@app.route("/api/pedidos/<int:item_id>", methods=["GET"])
def obter_pedido(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id, id_produto, quantidade, subtotal, data_pedido FROM pedidos WHERE id = ?",
        (item_id,)
    ).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Pedido não encontrado"}), 404
    return jsonify(dict(linha))

@app.route("/api/pedidos", methods=["POST"])
def adicionar_pedido():
    dados = request.get_json()
    conn = get_db_connection()
    conn.execute("INSERT INTO pedidos (id_produto, quantidade, subtotal, data_pedido) VALUES (?, ?, ?, ?)",
                 (dados["id_produto"], dados["quantidade"], dados["subtotal"], dados["data_pedido"]))
    conn.commit()
    conn.close()
    return jsonify({"id": conn.lastrowid}), 201

@app.route("/api/favoritos", methods=["GET"])
def listar_favoritos():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, id_produto FROM favoritos").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])

@app.route("/api/favoritos", methods=["POST"])
def adicionar_favorito():
    dados = request.get_json()
    conn = get_db_connection()
    conn.execute("INSERT INTO favoritos (id_produto) VALUES (?)", (dados["id_produto"],))
    conn.commit()
    conn.close()
    return jsonify({"id": conn.lastrowid}), 201

@app.route("/api/favoritos/<int:item_id>", methods=["GET"])
def obter_favorito(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id, id_produto FROM favoritos WHERE id = ?",
        (item_id,)
    ).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Favorito não encontrado"}), 404
    return jsonify(dict(linha))

if __name__ == "__main__":
    inicializar_banco()
    porta = int(os.environ.get("PORT", 5000))
    app.run(debug=False, port=porta)