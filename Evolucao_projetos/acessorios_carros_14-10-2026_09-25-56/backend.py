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


@app.route("/api/produtos", methods=["GET"])
def listar_produtos():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, nome, descricao, preco, imagem FROM produtos").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/produtos/<int:item_id>", methods=["GET"])
def obter_produtos(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id, nome, descricao, preco, imagem FROM produtos WHERE id = ?", (item_id,)
    ).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Registro não encontrado"}), 404
    return jsonify(dict(linha))


@app.route("/api/produtos", methods=["POST"])
def criar_produtos():
    dados = request.get_json(silent=True) or {}
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO produtos (nome, descricao, preco, imagem) VALUES (?, ?, ?, ?)",
            (dados.get("nome"), dados.get("descricao"), dados.get("preco"), dados.get("imagem"),)
        )
        conn.commit()
    except sqlite3.IntegrityError as erro:
        conn.close()
        return jsonify({"erro": str(erro)}), 400
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": novo_id}), 201


@app.route("/api/carrinho", methods=["GET"])
def listar_carrinho():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, produto_id, quantidade FROM carrinho").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/carrinho/<int:item_id>", methods=["GET"])
def obter_carrinho(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id, produto_id, quantidade FROM carrinho WHERE id = ?", (item_id,)
    ).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Registro não encontrado"}), 404
    return jsonify(dict(linha))


@app.route("/api/carrinho", methods=["POST"])
def criar_carrinho():
    dados = request.get_json(silent=True) or {}
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO carrinho (produto_id, quantidade) VALUES (?, ?)",
            (dados.get("produto_id"), dados.get("quantidade"),)
        )
        conn.commit()
    except sqlite3.IntegrityError as erro:
        conn.close()
        return jsonify({"erro": str(erro)}), 400
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": novo_id}), 201


@app.route("/api/ordens", methods=["GET"])
def listar_ordens():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, data, status FROM ordens").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/ordens/<int:item_id>", methods=["GET"])
def obter_ordens(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id, data, status FROM ordens WHERE id = ?", (item_id,)
    ).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Registro não encontrado"}), 404
    return jsonify(dict(linha))


@app.route("/api/ordens", methods=["POST"])
def criar_ordens():
    dados = request.get_json(silent=True) or {}
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO ordens (data, status) VALUES (?, ?)",
            (dados.get("data"), dados.get("status"),)
        )
        conn.commit()
    except sqlite3.IntegrityError as erro:
        conn.close()
        return jsonify({"erro": str(erro)}), 400
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": novo_id}), 201


@app.route("/api/logotipo", methods=["GET"])
def listar_logotipo():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, imagem FROM logotipo").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/logotipo/<int:item_id>", methods=["GET"])
def obter_logotipo(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id, imagem FROM logotipo WHERE id = ?", (item_id,)
    ).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Registro não encontrado"}), 404
    return jsonify(dict(linha))


@app.route("/api/logotipo", methods=["POST"])
def criar_logotipo():
    dados = request.get_json(silent=True) or {}
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO logotipo (imagem) VALUES (?)",
            (dados.get("imagem"),)
        )
        conn.commit()
    except sqlite3.IntegrityError as erro:
        conn.close()
        return jsonify({"erro": str(erro)}), 400
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": novo_id}), 201


@app.route("/api/menu", methods=["GET"])
def listar_menu():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, nome, imagem FROM menu").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/menu/<int:item_id>", methods=["GET"])
def obter_menu(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id, nome, imagem FROM menu WHERE id = ?", (item_id,)
    ).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Registro não encontrado"}), 404
    return jsonify(dict(linha))


@app.route("/api/menu", methods=["POST"])
def criar_menu():
    dados = request.get_json(silent=True) or {}
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO menu (nome, imagem) VALUES (?, ?)",
            (dados.get("nome"), dados.get("imagem"),)
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
