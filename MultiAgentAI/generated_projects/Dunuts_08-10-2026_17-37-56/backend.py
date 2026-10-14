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


@app.route("/api/diagramas", methods=["GET"])
def listar_diagramas():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, nome, conteúdo FROM diagramas").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/diagramas/<int:item_id>", methods=["GET"])
def obter_diagrama(item_id):
    conn = get_db_connection()
    linha = conn.execute("SELECT id, nome, conteúdo FROM diagramas WHERE id = ?", (item_id,))
    conn.close()
    if linha is None:
        return jsonify({"erro": "Diagrama não encontrado"}), 404
    return jsonify(dict(linha))


@app.route("/api/diagramas", methods=["POST"])
def criar_diagrama():
    dados = request.get_json()
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO diagramas (nome, conteúdo) VALUES (?, ?)",
        (dados["nome"], dados["conteúdo"])
    )
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": novo_id}), 201


@app.route("/api/nomes", methods=["GET"])
def listar_nomes():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, tipo, nome FROM nomes").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/nomes/<int:item_id>", methods=["GET"])
def obter_nome(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id, tipo, nome FROM nomes WHERE id = ?",
        (item_id,)
    ).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Nome não encontrado"}), 404
    return jsonify(dict(linha))


@app.route("/api/nomes", methods=["POST"])
def criar_nome():
    dados = request.get_json()
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO nomes (tipo, nome) VALUES (?, ?)",
        (dados["tipo"], dados["nome"])
    )
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": novo_id}), 201


@app.route("/api/conteúdo", methods=["GET"])
def listar_conteúdo():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, nome, quantidade, preço FROM conteúdo").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/conteúdo/<int:item_id>", methods=["GET"])
def obter_conteúdo(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id, nome, quantidade, preço FROM conteúdo WHERE id = ?",
        (item_id,)
    ).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Conteúdo não encontrado"}), 404
    return jsonify(dict(linha))


@app.route("/api/conteúdo", methods=["POST"])
def criar_conteúdo():
    dados = request.get_json()
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO conteúdo (nome, quantidade, preço) VALUES (?, ?, ?)",
        (dados["nome"], dados["quantidade"], dados["preço"])
    )
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": novo_id}), 201


if __name__ == "__main__":
    inicializar_banco()
    porta = int(os.environ.get("PORT", 5000))
    app.run(debug=False, port=porta)