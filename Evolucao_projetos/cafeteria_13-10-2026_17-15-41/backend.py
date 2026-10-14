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
    linhas = conn.execute("SELECT id, nome, descricao, categoria, preco, imagem FROM produtos").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/produtos/<int:item_id>", methods=["GET"])
def obter_produtos(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id, nome, descricao, categoria, preco, imagem FROM produtos WHERE id = ?", (item_id,)
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
            "INSERT INTO produtos (nome, descricao, categoria, preco, imagem) VALUES (?, ?, ?, ?, ?)",
            (dados.get("nome"), dados.get("descricao"), dados.get("categoria"), dados.get("preco"), dados.get("imagem"),)
        )
        conn.commit()
    except sqlite3.IntegrityError as erro:
        conn.close()
        return jsonify({"erro": str(erro)}), 400
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": novo_id}), 201


@app.route("/api/unidades", methods=["GET"])
def listar_unidades():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, nome, endereco, bairro, horario FROM unidades").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/unidades/<int:item_id>", methods=["GET"])
def obter_unidades(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id, nome, endereco, bairro, horario FROM unidades WHERE id = ?", (item_id,)
    ).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Registro não encontrado"}), 404
    return jsonify(dict(linha))


@app.route("/api/unidades", methods=["POST"])
def criar_unidades():
    dados = request.get_json(silent=True) or {}
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO unidades (nome, endereco, bairro, horario) VALUES (?, ?, ?, ?)",
            (dados.get("nome"), dados.get("endereco"), dados.get("bairro"), dados.get("horario"),)
        )
        conn.commit()
    except sqlite3.IntegrityError as erro:
        conn.close()
        return jsonify({"erro": str(erro)}), 400
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": novo_id}), 201


@app.route("/api/pedidos", methods=["GET"])
def listar_pedidos():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, produto_id, quantidade, status FROM pedidos").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/pedidos/<int:item_id>", methods=["GET"])
def obter_pedidos(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id, produto_id, quantidade, status FROM pedidos WHERE id = ?", (item_id,)
    ).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Registro não encontrado"}), 404
    return jsonify(dict(linha))


@app.route("/api/pedidos", methods=["POST"])
def criar_pedidos():
    dados = request.get_json(silent=True) or {}
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO pedidos (produto_id, quantidade, status) VALUES (?, ?, ?)",
            (dados.get("produto_id"), dados.get("quantidade"), dados.get("status"),)
        )
        conn.commit()
    except sqlite3.IntegrityError as erro:
        conn.close()
        return jsonify({"erro": str(erro)}), 400
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": novo_id}), 201


@app.route("/api/categorias", methods=["GET"])
def listar_categorias():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, nome FROM categorias").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/categorias/<int:item_id>", methods=["GET"])
def obter_categorias(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id, nome FROM categorias WHERE id = ?", (item_id,)
    ).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Registro não encontrado"}), 404
    return jsonify(dict(linha))


@app.route("/api/categorias", methods=["POST"])
def criar_categorias():
    dados = request.get_json(silent=True) or {}
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO categorias (nome) VALUES (?)",
            (dados.get("nome"),)
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
