"""Backend Flask do site, montado a partir do database/schema.sql.

O banco (database.db) é criado na primeira execução, lendo o arquivo
database/schema.sql. Cada tabela do esquema ganha rotas em /api/<tabela>.
"""
from flask import Flask, jsonify, request
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")

# static_url_path="" faz o Flask servir style.css e script.js na raiz do site
app = Flask(__name__, static_folder="static", static_url_path="")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_banco():
    # Cria o banco só na primeira vez, executando o schema.sql
    if os.path.exists(DB_PATH) and os.path.getsize(DB_PATH) > 0:
        return

    conn = get_db_connection()
    try:
        with open(SCHEMA_PATH, encoding="utf-8") as arquivo:
            conn.executescript(arquivo.read())
        conn.commit()
    except sqlite3.Error:
        # não deixa um database.db pela metade (senão a próxima execução
        # acharia que o banco já existe e pularia a criação)
        conn.close()
        os.remove(DB_PATH)
        raise
    conn.close()


@app.route("/")
def home():
    return app.send_static_file("index.html")


@app.route("/api/produto", methods=["GET"])
def listar_produto():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id_produto, nome, imagem, descricao_produto, preco_produto, avaliacao_produto FROM produto").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/produto/<int:item_id>", methods=["GET"])
def obter_produto(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id_produto, nome, imagem, descricao_produto, preco_produto, avaliacao_produto FROM produto WHERE id_produto = ?", (item_id,)
    ).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Registro não encontrado"}), 404
    return jsonify(dict(linha))


@app.route("/api/produto", methods=["POST"])
def criar_produto():
    dados = request.get_json(silent=True) or {}
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO produto (nome, imagem, descricao_produto, preco_produto, avaliacao_produto) VALUES (?, ?, ?, ?, ?)",
            (dados.get("nome"), dados.get("imagem"), dados.get("descricao_produto"), dados.get("preco_produto"), dados.get("avaliacao_produto"),)
        )
        conn.commit()
    except sqlite3.IntegrityError as erro:
        conn.close()
        return jsonify({"erro": str(erro)}), 400
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": novo_id}), 201


@app.route("/api/pedido", methods=["GET"])
def listar_pedido():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id_pedido, id_produto, quantidade, subtotal, data_pedido FROM pedido").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/pedido/<int:item_id>", methods=["GET"])
def obter_pedido(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id_pedido, id_produto, quantidade, subtotal, data_pedido FROM pedido WHERE id_pedido = ?", (item_id,)
    ).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Registro não encontrado"}), 404
    return jsonify(dict(linha))


@app.route("/api/pedido", methods=["POST"])
def criar_pedido():
    dados = request.get_json(silent=True) or {}
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO pedido (id_produto, quantidade, subtotal, data_pedido) VALUES (?, ?, ?, ?)",
            (dados.get("id_produto"), dados.get("quantidade"), dados.get("subtotal"), dados.get("data_pedido"),)
        )
        conn.commit()
    except sqlite3.IntegrityError as erro:
        conn.close()
        return jsonify({"erro": str(erro)}), 400
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": novo_id}), 201


@app.route("/api/favorito", methods=["GET"])
def listar_favorito():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id_favorito, id_produto, data_favorito FROM favorito").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/favorito/<int:item_id>", methods=["GET"])
def obter_favorito(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id_favorito, id_produto, data_favorito FROM favorito WHERE id_favorito = ?", (item_id,)
    ).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Registro não encontrado"}), 404
    return jsonify(dict(linha))


@app.route("/api/favorito", methods=["POST"])
def criar_favorito():
    dados = request.get_json(silent=True) or {}
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO favorito (id_produto, data_favorito) VALUES (?, ?)",
            (dados.get("id_produto"), dados.get("data_favorito"),)
        )
        conn.commit()
    except sqlite3.IntegrityError as erro:
        conn.close()
        return jsonify({"erro": str(erro)}), 400
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": novo_id}), 201


if __name__ == "__main__":
    inicializar_banco()
    porta = int(os.environ.get("PORT", 5000))
    app.run(debug=False, port=porta)
