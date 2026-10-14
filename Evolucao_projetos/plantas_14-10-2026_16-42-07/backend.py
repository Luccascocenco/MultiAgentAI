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


@app.route("/api/plantas", methods=["GET"])
def listar_plantas():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, nome, descricao, preco FROM plantas").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/plantas/<int:item_id>", methods=["GET"])
def obter_planta(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id, nome, descricao, preco FROM plantas WHERE id = ?",
        (item_id,)
    ).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Planta não encontrada"}), 404
    return jsonify(dict(linha))


@app.route("/api/plantas", methods=["POST"])
def criar_planta():
    dados = request.get_json()
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO plantas (nome, descricao, preco) VALUES (?, ?, ?)",
        (dados["nome"], dados.get("descricao"), dados["preco"])
    )
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": novo_id}), 201


@app.route("/api/vasos", methods=["GET"])
def listar_vasos():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, tipo, tamanho, preco FROM vasos").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/vasos/<int:item_id>", methods=["GET"])
def obter_vaso(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id, tipo, tamanho, preco FROM vasos WHERE id = ?",
        (item_id,)
    ).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Vaso não encontrado"}), 404
    return jsonify(dict(linha))


@app.route("/api/vasos", methods=["POST"])
def criar_vaso():
    dados = request.get_json()
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO vasos (tipo, tamanho, preco) VALUES (?, ?, ?)",
        (dados["tipo"], dados["tamanho"], dados["preco"])
    )
    conn.commit()
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
def obterproduto(item_id):
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
def criarproduto():
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


@app.route("/api/compras", methods=["GET"])
def listar_compras():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, planta_id, vaso_id, produto_id, quantidade, preco FROM compras").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/compras/<int:item_id>", methods=["GET"])
def obter_compra(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id, planta_id, vaso_id, produto_id, quantidade, preco FROM compras WHERE id = ?",
        (item_id,)
    ).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Compra não encontrada"}), 404
    return jsonify(dict(linha))


@app.route("/api/compras", methods=["POST"])
def criar_compra():
    dados = request.get_json()
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO compras (planta_id, vaso_id, produto_id, quantidade, preco) VALUES (?, ?, ?, ?, ?)",
        (dados["planta_id"], dados["vaso_id"], dados["produto_id"], dados["quantidade"], dados["preco"])
    )
    conn.commit()
    conn.close()
    return jsonify({"id": cursor.lastrowid}), 201


if __name__ == "__main__":
    inicializar_banco()
    porta = int(os.environ.get("PORT", 5000))
    app.run(debug=False, port=porta)