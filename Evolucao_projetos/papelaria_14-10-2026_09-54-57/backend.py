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

inicializar_banco()

@app.route("/")
def home():
    return app.send_static_file("index.html")

@app.route("/api/produtos", methods=["GET"])
def listar_produtos():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, nome, descricao, preco FROM produtos").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])

@app.route("/api/produtos/<int:item_id>", methods=["GET"])
def obter_produto(item_id):
    conn = get_db_connection()
    linha = conn.execute("SELECT id, nome, descricao, preco FROM produtos WHERE id = ?", (item_id,)).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Produto não encontrado"}), 404
    return jsonify(dict(linha))

@app.route("/api/produtos", methods=["POST"])
def criar_produto():
    dados = request.get_json()
    conn = get_db_connection()
    cursor = conn.execute("INSERT INTO produtos (nome, descricao, preco) VALUES (?, ?, ?)", (dados["nome"], dados.get("descricao"), dados["preco"]))
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": novo_id}), 201

@app.route("/api/pedidos", methods=["GET"])
def listar_pedidos():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, produto_id, quantidade, preco_total FROM pedidos").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])

@app.route("/api/pedidos/<int:item_id>", methods=["GET"])
def obter_pedido(item_id):
    conn = get_db_connection()
    linha = conn.execute("SELECT id, produto_id, quantidade, preco_total FROM pedidos WHERE id = ?", (item_id,)).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Pedido não encontrado"}), 404
    return jsonify(dict(linha))

@app.route("/api/carrinho", methods=["GET"])
def obter_carrinho():
    conn = get_db_connection()
    linhas = conn.execute("SELECT produto_id, quantidade FROM carrinho").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(debug=False, port=porta)