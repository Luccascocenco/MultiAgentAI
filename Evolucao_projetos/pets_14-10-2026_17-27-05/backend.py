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
    produtos = conn.execute("SELECT id, nome, imagem, preco, avaliacao FROM produtos").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in produtos])


@app.route("/api/produtos/<int:item_id>", methods=["GET"])
def obter_produto(item_id):
    conn = get_db_connection()
    produto = conn.execute(
        "SELECT id, nome, imagem, preco, avaliacao FROM produtos WHERE id = ?",
        (item_id,)
    ).fetchone()
    conn.close()
    if produto is None:
        return jsonify({"erro": "Produto não encontrado"}), 404
    return jsonify(dict(produto))


@app.route("/api/carrinho", methods=["GET"])
def show_carrinho():
    conn = get_db_connection()
    carrinho = conn.execute("SELECT id_produto, quantidade FROM carrinho").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in carrinho])


@app.route("/api/carrinho/<int:id_produto>", methods=["GET"])
def atualizar_carrinho(id_produto):
    conn = get_db_connection()
    quantidade = conn.execute(
        "SELECT quantidade FROM carrinho WHERE id_produto = ?",
        (id_produto,)
    ).fetchone()
    conn.close()
    if quantidade is None:
        return jsonify({"erro": "Quantidade não encontrada"}), 404
    return jsonify({"quantidade": quantidade[0] + 1})


@app.route("/api/ordens", methods=["POST"])
def criar_ordem():
    dados = request.get_json()
    conn = get_db_connection()
    conn.execute("INSERT INTO ordens (id_usuario, data, total, status) VALUES (?, ?, ?, ?)", (
        dados["id_usuario"], dados["data"], dados["total"], "em_processo"
    ))
    conn.commit()
    conn.close()
    return jsonify({"id": conn.lastrowid}), 201


if __name__ == "__main__":
    inicializar_banco()
    porta = int(os.environ.get("PORT", 5000))
    app.run(debug=False, port=porta)