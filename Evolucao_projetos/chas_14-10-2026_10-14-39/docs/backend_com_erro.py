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

inicializar_banco()

@app.route("/")
def home():
    return app.send_static_file("index.html")

@app.route("/api/produtos", methods=["GET"])
def listar_produtos():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, nome, preco, descricao FROM produtos").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])

@app.route("/api/produtos/<int:item_id>", methods=["GET"])
def obter_produto(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id, nome, preco, descricao FROM produtos WHERE id = ?",
        (item_id,)
    ).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Produto não encontrado"}), 404
    return jsonify(dict(linha))

@app.route("/api/produtos", methods=["POST"])
def criar_produto():
    dados = request.get_json()
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO produtos (nome, preco, descricao) VALUES (?, ?, ?)",
        (dados["nome"], dados.get("preco"), dados["descricao"])
    )
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": novo_id}), 201

@app.route("/api/produtos/:id", methods=["PUT"])
def atualizar_produto(item_id):
    dados = request.get_json()
    conn = get_db_connection()
    cursor = conn.execute(
        "UPDATE produtos SET nome = ?, preco = ?, descricao = ? WHERE id = ?",
        (dados["nome"], dados.get("preco"), dados["descricao"], item_id)
    )
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Produto atualizado com sucesso"})

@app.route("/api/produtos/:id", methods=["DELETE"])
def deletar_produto(item_id):
    conn = get_db_connection()
    cursor = conn.execute("DELETE FROM produtos WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Produto deletado com sucesso"})

@app.route("/api/produtos/categorias", methods=["GET"])
def listar_categorias():
    conn = get_db_connection()
    linhas = conn.execute("SELECT id, nome, descricao FROM categorias").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])

@app.route("/api/produtos/categorias/<int:item_id>", methods=["GET"])
def obter_categoria(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT id, nome, descricao FROM categorias WHERE id = ?",
        (item_id,)
    ).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Categoria não encontrada"}), 404
    return jsonify(dict(linha))

@app.route("/api/produtos/categorias", methods=["POST"])
def criar_categoria():
    dados = request.get_json()
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO categorias (nome, descricao) VALUES (?, ?)",
        (dados["nome"], dados["descricao"])
    )
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": novo_id}), 201

@app.route("/api/produtos/categorias/:id", methods=["PUT"])
def atualizar_categoria(item_id):
    dados = request.get_json()
    conn = get_db_connection()
    cursor = conn.execute(
        "UPDATE categorias SET nome = ?, descricao = ? WHERE id = ?",
        (dados["nome"], dados["descricao"], item_id)
    )
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Categoria atualizada com sucesso"})

@app.route("/api/produtos/categorias/:id", methods=["DELETE"])
def deletar_categoria(item_id):
    conn = get_db_connection()
    cursor = conn.execute("DELETE FROM categorias WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Categoria deletada com sucesso"})

@app.route("/api/produtos/:id/produtos", methods=["POST"])
def adicionar_produto_a_categoria(item_id):
    dados = request.get_json()
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO categorias_produtos (produto_id, categoria_id) VALUES (?, ?)",
        (item_id, dados["categoria_id"])
    )
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Produto adicionado à categoria com sucesso"})

@app.route("/api/produtos/:id/produtos", methods=["DELETE"])
def remover_produto_a_categoria(item_id):
    conn = get_db_connection()
    cursor = conn.execute("DELETE FROM categorias_produtos WHERE produto_id = ?", (item_id,))
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Produto removido da categoria com sucesso"})

@app.route("/api/produtos/:id/pedidos", methods=["POST"])
def adicionar_pedido(item_id):
    dados = request.get_json()
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO pedidos (data, produto_id, quantidade) VALUES (?, ?, ?)",
        (dados["data"], item_id, dados["quantidade"])
    )
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Pedido adicionado com sucesso"})

@app.route("/api/produtos/:id/pedidos", methods=["DELETE"])
def remover_pedido(item_id):
    conn = get_db_connection()
    cursor = conn.execute("DELETE FROM pedidos WHERE produto_id = ?", (item_id,))
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Pedido removido com sucesso"})

@app.route("/api/produtos/:id/pedidos", methods=["GET"])
def listar_pedidos(item_id):
    conn = get_db_connection()
    linhas = conn.execute("SELECT data, quantidade FROM pedidos WHERE produto_id = ?", (item_id,)).fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])

@app.route("/api/produtos/:id/pedidos", methods=["PUT"])
def atualizar_pedido(item_id):
    dados = request.get_json()
    conn = get_db_connection()
    cursor = conn.execute(
        "UPDATE pedidos SET data = ?, quantidade = ? WHERE id = ?",
        (dados["data"], dados["quantidade"], item_id)
    )
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Pedido atualizado com sucesso"})

@app.route("/api/produtos/:id/pedidos", methods=["DELETE"])
def remover_pedido(item_id):
    conn = get_db_connection()
    cursor = conn.execute("DELETE FROM pedidos WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Pedido removido com sucesso"})

@app.route("/api/produtos", methods=["DELETE"])
def deletar_todos_produto():
    conn = get_db_connection()
    cursor = conn.execute("DELETE FROM produtos")
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Todos os produtos deletados com sucesso"})

@app.route("/api/produtos", methods=["DELETE"])
def deletar_todos_categoria():
    conn = get_db_connection()
    cursor = conn.execute("DELETE FROM categorias")
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Todas as categorias deletadas com sucesso"})

@app.route("/api/produtos", methods=["DELETE"])
def deletar_todos_pedido():
    conn = get_db_connection()
    cursor = conn.execute("DELETE FROM pedidos")
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Todas as pedidos deletadas com sucesso"})

if __name__ == "__main__":
    app.run(debug=False, port=5000)