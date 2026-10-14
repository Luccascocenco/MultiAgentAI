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
    linha = conn.execute(
        "SELECT id, nome, descricao, preco FROM produtos WHERE id = ?",
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
    cursor = conn.execute(
        "INSERT INTO produtos (nome, descricao, preco) VALUES (?, ?, ?)",
        (dados["nome"], dados.get("descricao"), dados["preco"])
    )
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": novo_id}), 201

@app.route("/api/produtos/<int:item_id>/quantidade", methods=["PUT"])
def atualizar_quantidade(item_id):
    dados = request.get_json()
    conn = get_db_connection()
    cursor = conn.execute(
        "UPDATE carrinho SET quantidade = ? WHERE id_produto = ?",
        (dados["quantidade"], item_id)
    )
    conn.commit()
    conn.close()
    return jsonify({"quantidade": dados["quantidade"]})

@app.route("/api/cart", methods=["GET"])
def get_cart():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, id_produto, quantidade FROM carrinho").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])

@app.route("/api/cart", methods=["POST"])
def atualizar_cart():
    dados = request.get_json()
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO carrinho (id_produto, quantidade) VALUES (?, ?)",
        (dados["id_produto"], dados["quantidade"])
    )
    conn.commit()
    conn.close()
    return jsonify({"id": cursor.lastrowid})

@app.route("/api/payment", methods=["GET"])
def get_payment():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, id_produto, data FROM pedidos").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])

@app.route("/api/payment", methods=["POST"])
def realizar_pagamento():
    dados = request.get_json()
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO pedidos (id_produto, data, total) VALUES (?, ?, ?)",
        (dados["id_produto"], dados["data"], dados["total"])
    )
    conn.commit()
    conn.close()
    return jsonify({"id": cursor.lastrowid})

@app.route("/api/contact", methods=["POST"])
def enviar_mensagem_contato():
    dados = request.get_json()
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO mensagens_contato (nome, email, mensagem, data) VALUES (?, ?, ?, ?)",
        (dados["nome"], dados["email"], dados["mensagem"], dados["data"])
    )
    conn.commit()
    conn.close()
    return jsonify({"id": cursor.lastrowid})

@app.route("/api/error", methods=["GET"])
def get_error():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, nome FROM acoes").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])

@app.route("/api/error", methods=["POST"])
def handle_error():
    dados = request.get_json()
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO acoes (nome) VALUES (?)",
        (dados["nome"],)
    )
    conn.commit()
    conn.close()
    return jsonify({"id": cursor.lastrowid})

if __name__ == "__main__":
    inicializar_banco()
    porta = int(os.environ.get("PORT", 5000))
    app.run(debug=False, port=porta)