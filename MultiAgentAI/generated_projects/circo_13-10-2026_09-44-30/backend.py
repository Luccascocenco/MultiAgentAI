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
    linhas = conn.execute("SELECT id, nome, descricao, categoria, imagem FROM diagramas").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/diagramas/<int:item_id>", methods=["GET"])
def obter_diagramas(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id, nome, descricao, categoria, imagem FROM diagramas WHERE id = ?", (item_id,)
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
            "INSERT INTO diagramas (nome, descricao, categoria, imagem) VALUES (?, ?, ?, ?)",
            (dados.get("nome"), dados.get("descricao"), dados.get("categoria"), dados.get("imagem"),)
        )
        conn.commit()
    except sqlite3.IntegrityError as erro:
        conn.close()
        return jsonify({"erro": str(erro)}), 400
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": novo_id}), 201


@app.route("/api/ingressos", methods=["GET"])
def listar_ingressos():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, diagrama_id, data, preco, status FROM ingressos").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/ingressos/<int:item_id>", methods=["GET"])
def obter_ingressos(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id, diagrama_id, data, preco, status FROM ingressos WHERE id = ?", (item_id,)
    ).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Registro não encontrado"}), 404
    return jsonify(dict(linha))


@app.route("/api/ingressos", methods=["POST"])
def criar_ingressos():
    dados = request.get_json(silent=True) or {}
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO ingressos (diagrama_id, data, preco, status) VALUES (?, ?, ?, ?)",
            (dados.get("diagrama_id"), dados.get("data"), dados.get("preco"), dados.get("status"),)
        )
        conn.commit()
    except sqlite3.IntegrityError as erro:
        conn.close()
        return jsonify({"erro": str(erro)}), 400
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": novo_id}), 201


@app.route("/api/users", methods=["GET"])
def listar_users():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, nome, email FROM users").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/users/<int:item_id>", methods=["GET"])
def obter_users(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id, nome, email FROM users WHERE id = ?", (item_id,)
    ).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Registro não encontrado"}), 404
    return jsonify(dict(linha))


@app.route("/api/users", methods=["POST"])
def criar_users():
    dados = request.get_json(silent=True) or {}
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO users (nome, email, senha) VALUES (?, ?, ?)",
            (dados.get("nome"), dados.get("email"), dados.get("senha"),)
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
