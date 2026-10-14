from flask import Flask, jsonify, request
import sqlite3
import os

app = Flask(__name__, static_folder="static", static_url_path="")

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_banco():
    # Cria o banco a partir do schema.sql, só na primeira vez
    if os.path.exists("database.db") and os.path.getsize("database.db") > 0:
        return

    conn = get_db_connection()
    with open("database/schema.sql", encoding="utf-8") as arquivo:
        conn.executescript(arquivo.read())
    conn.commit()
    conn.close()


@app.route("/")
def home():
    return app.send_static_file("index.html")


@app.route("/api/pedidos", methods=["GET"])
def listar_pedidos():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, cliente, itens, total FROM pedidos").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/pedidos/<int:item_id>", methods=["GET"])
def obter_pedido(item_id):
    conn = get_db_connection()
    linha = conn.execute("SELECT id, cliente, itens, total FROM pedidos WHERE id = ?", (item_id,))
    conn.close()
    if linha is None:
        return jsonify({"erro": "Pedido não encontrado"}), 404
    return jsonify(dict(linha))


@app.route("/api/pedidos", methods=["POST"])
def criar_pedido():
    dados = request.get_json()
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO pedidos (cliente, itens, total) VALUES (?, ?, ?)",
        (dados["cliente"], dados["itens"], dados["total"])
    )
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": novo_id}), 201


@app.route("/api.itens", methods=["GET"])
def listar_itens():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, nome, preco FROM itens").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api.itens/<int:item_id>", methods=["GET"])
def obter_item(item_id):
    conn = get_db_connection()
    linha = conn.execute("SELECT id, nome, preco FROM itens WHERE id = ?", (item_id,))
    conn.close()
    if linha is None:
        return jsonify({"erro": "Item não encontrado"}), 404
    return jsonify(dict(linha))


@app.route("/api.itens", methods=["POST"])
def criar_item():
    dados = request.get_json()
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO itens (nome, preco) VALUES (?, ?)",
        (dados["nome"], dados["preco"])
    )
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": novo_id}), 201


@app.route("/api.esmaltes", methods=["GET"])
def listar_esmaltes():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, nome, cor FROM esmaltes").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api.esmaltes/<int:item_id>", methods=["GET"])
def obter_esmalte(item_id):
    conn = get_db_connection()
    linha = conn.execute("SELECT id, nome, cor FROM esmaltes WHERE id = ?", (item_id,))
    conn.close()
    if linha is None:
        return jsonify({"erro": "Esmalte não encontrado"}), 404
    return jsonify(dict(linha))


@app.route("/api.esmaltes", methods=["POST"])
def criar_esmalte():
    dados = request.get_json()
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO esmaltes (nome, cor) VALUES (?, ?)",
        (dados["nome"], dados["cor"])
    )
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": novo_id}), 201


if __name__ == "__main__":
    inicializar_banco()
    porta = int(os.environ.get("PORT", 5000))
    app.run(debug=False, port=porta)