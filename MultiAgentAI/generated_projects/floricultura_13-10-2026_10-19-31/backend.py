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


@app.route("/api/diagramas", methods=["GET"])
def listar_diagramas():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, nome, conteudo FROM diagramas").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/diagramas/<int:item_id>", methods=["GET"])
def obter_diagramas(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id, nome, conteudo FROM diagramas WHERE id = ?", (item_id,)
    ).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Registro não encontrado"}), 404
    return jsonify(dict(linha))


@app.route("/api/diagramas", methods=["POST"])
def criar_diagramas():
    dados = request.get_json(silent=True) or {}
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO diagramas (nome, conteudo) VALUES (?, ?)",
            (dados.get("nome"), dados.get("conteudo"),)
        )
        conn.commit()
    except sqlite3.IntegrityError as erro:
        conn.close()
        return jsonify({"erro": str(erro)}), 400
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": novo_id}), 201


@app.route("/api/produtos", methods=["GET"])
def listar_produtos():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, nome, descricao, preco FROM produtos").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/produtos/<int:item_id>", methods=["GET"])
def obter_produtos(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id, nome, descricao, preco FROM produtos WHERE id = ?", (item_id,)
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
            "INSERT INTO produtos (nome, descricao, preco) VALUES (?, ?, ?)",
            (dados.get("nome"), dados.get("descricao"), dados.get("preco"),)
        )
        conn.commit()
    except sqlite3.IntegrityError as erro:
        conn.close()
        return jsonify({"erro": str(erro)}), 400
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": novo_id}), 201


@app.route("/api/compras", methods=["GET"])
def listar_compras():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, id_produto, data_compra, quantidade FROM compras").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/compras/<int:item_id>", methods=["GET"])
def obter_compras(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id, id_produto, data_compra, quantidade FROM compras WHERE id = ?", (item_id,)
    ).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Registro não encontrado"}), 404
    return jsonify(dict(linha))


@app.route("/api/compras", methods=["POST"])
def criar_compras():
    dados = request.get_json(silent=True) or {}
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO compras (id_produto, data_compra, quantidade) VALUES (?, ?, ?)",
            (dados.get("id_produto"), dados.get("data_compra"), dados.get("quantidade"),)
        )
        conn.commit()
    except sqlite3.IntegrityError as erro:
        conn.close()
        return jsonify({"erro": str(erro)}), 400
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": novo_id}), 201


@app.route("/api/imagens", methods=["GET"])
def listar_imagens():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, nome, imagem, produto_id FROM imagens").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/imagens/<int:item_id>", methods=["GET"])
def obter_imagens(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id, nome, imagem, produto_id FROM imagens WHERE id = ?", (item_id,)
    ).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Registro não encontrado"}), 404
    return jsonify(dict(linha))


@app.route("/api/imagens", methods=["POST"])
def criar_imagens():
    dados = request.get_json(silent=True) or {}
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO imagens (nome, imagem, produto_id) VALUES (?, ?, ?)",
            (dados.get("nome"), dados.get("imagem"), dados.get("produto_id"),)
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
