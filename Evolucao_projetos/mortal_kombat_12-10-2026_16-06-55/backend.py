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
    with open(SCHEMA_PATH, encoding="utf-8") as arquivo:
        conn.executescript(arquivo.read())
    conn.commit()
    conn.close()


@app.route("/")
def home():
    return app.send_static_file("index.html")


@app.route("/api/usuarios", methods=["GET"])
def listar_usuarios():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, nome, email FROM usuarios").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/usuarios/<int:item_id>", methods=["GET"])
def obter_usuarios(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id, nome, email FROM usuarios WHERE id = ?", (item_id,)
    ).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Registro não encontrado"}), 404
    return jsonify(dict(linha))


@app.route("/api/usuarios", methods=["POST"])
def criar_usuarios():
    dados = request.get_json(silent=True) or {}
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
            (dados.get("nome"), dados.get("email"), dados.get("senha"),)
        )
        conn.commit()
    except sqlite3.IntegrityError as erro:
        conn.close()
        return jsonify({"erro": str(erro)}), 400
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": novo_id}), 201


@app.route("/api/jogos", methods=["GET"])
def listar_jogos():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, nome, conteudo, preco FROM jogos").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/jogos/<int:item_id>", methods=["GET"])
def obter_jogos(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id, nome, conteudo, preco FROM jogos WHERE id = ?", (item_id,)
    ).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Registro não encontrado"}), 404
    return jsonify(dict(linha))


@app.route("/api/jogos", methods=["POST"])
def criar_jogos():
    dados = request.get_json(silent=True) or {}
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO jogos (nome, conteudo, preco) VALUES (?, ?, ?)",
            (dados.get("nome"), dados.get("conteudo"), dados.get("preco"),)
        )
        conn.commit()
    except sqlite3.IntegrityError as erro:
        conn.close()
        return jsonify({"erro": str(erro)}), 400
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": novo_id}), 201


@app.route("/api/carrinhos", methods=["GET"])
def listar_carrinhos():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, usuario_id, jogo_id, quantidade FROM carrinhos").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/carrinhos/<int:item_id>", methods=["GET"])
def obter_carrinhos(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id, usuario_id, jogo_id, quantidade FROM carrinhos WHERE id = ?", (item_id,)
    ).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Registro não encontrado"}), 404
    return jsonify(dict(linha))


@app.route("/api/carrinhos", methods=["POST"])
def criar_carrinhos():
    dados = request.get_json(silent=True) or {}
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO carrinhos (usuario_id, jogo_id, quantidade) VALUES (?, ?, ?)",
            (dados.get("usuario_id"), dados.get("jogo_id"), dados.get("quantidade"),)
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
    linhas = conn.execute("SELECT id, usuario_id, jogo_id, quantidade, preco, data FROM compras").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/compras/<int:item_id>", methods=["GET"])
def obter_compras(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id, usuario_id, jogo_id, quantidade, preco, data FROM compras WHERE id = ?", (item_id,)
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
            "INSERT INTO compras (usuario_id, jogo_id, quantidade, preco, data) VALUES (?, ?, ?, ?, ?)",
            (dados.get("usuario_id"), dados.get("jogo_id"), dados.get("quantidade"), dados.get("preco"), dados.get("data"),)
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
