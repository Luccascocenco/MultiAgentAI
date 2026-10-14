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
    if os.path.exists(DB_PATH) and os.path.getsize(DB_PATH) > 0:
        return

    conn = get_db_connection()
    with open(SCHEMA_PATH, encoding="utf-8") as arquivo:
        conn.executescript(arquivo.read())
    conn.commit()
    conn.close()

@app.route("/", methods=["GET"])
def home():
    return app.send_static_file("index.html")

@app.route("/api/usuarios", methods=["GET"])
def listar_usuarios():
    conn = get_db_connection()
    usuarios = conn.execute("SELECT id, email, nome, sobrenome FROM usuarios").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in usuarios])

@app.route("/api/usuarios", methods=["POST"])
def criar_usuario():
    dados = request.get_json()
    conn = get_db_connection()
    conn.execute("INSERT INTO usuarios (email, senha, nome, sobrenome) VALUES (?, ?, ?, ?)", (dados["email"], dados["senha"], dados["nome"], dados["sobrenome"]))
    conn.commit()
    usuario_id = conn.lastrowid
    conn.close()
    return jsonify({"id": usuario_id})

@app.route("/api/produtos", methods=["GET"])
def listar_produtos():
    conn = get_db_connection()
    produtos = conn.execute("SELECT id, nome, descricao, preco, imagem FROM produtos").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in produtos])

@app.route("/api/carrinho", methods=["GET"])
def listar_carrinho():
    conn = get_db_connection()
    carrinho = conn.execute("SELECT id, produto_id, quantidade FROM carrinho").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in carrinho])

@app.route("/api/carrinho", methods=["POST"])
def adicionar_produto_carrinho():
    dados = request.get_json()
    conn = get_db_connection()
    conn.execute("INSERT INTO carrinho (produto_id, quantidade) VALUES (?, ?)", (dados["produto_id"], dados["quantidade"]))
    conn.commit()
    carrinho_id = conn.lastrowid
    conn.close()
    return jsonify({"id": carrinho_id})

@app.route("/api/carrinho", methods=["POST"])
def remover_produto_carrinho():
    dados = request.get_json()
    conn = get_db_connection()
    conn.execute("DELETE FROM carrinho WHERE id = ?", (dados["id"],))
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Produto removido do carrinho"})

@app.route("/api/carrinho/pagar", methods=["POST"])
def pagar_carrinho():
    dados = request.get_json()
    conn = get_db_connection()
    conn.execute("SELECT produto_id, quantidade FROM carrinho WHERE id = ?", (dados["id"],))
    produtos = conn.fetchall()
    for produto in produtos:
        conn.execute("UPDATE produtos SET estoque -= ? WHERE id = ?", (produto[1], produto[0]))
        conn.commit()
    conn.close()
    return jsonify({"mensagem": "Compra realizada com sucesso"})

if __name__ == "__main__":
    inicializar_banco()
    porta = int(os.environ.get("PORT", 5000))
    app.run(debug=False, port=porta)