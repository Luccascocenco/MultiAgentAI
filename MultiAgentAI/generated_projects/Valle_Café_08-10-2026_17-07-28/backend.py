from flask import Flask, request, jsonify
import sqlite3
import os
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")

app = Flask(__name__)

def get_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Error as e:
        print(e)
        return None

def inicializar_banco():
    conn = get_db_connection()
    if conn is not None:
        subprocess.check_call(['sqlite3', DB_PATH, 'import', SCHEMA_PATH])
        conn.close()

def criar_tabela_diagramas():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS diagramas (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            conteudo TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def criar_tabela_produtos():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY,
            diagrama_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            FOREIGN KEY (diagrama_id) REFERENCES diagramas (id)
        )
    ''')
    conn.commit()
    conn.close()

def criar_tabela_pedidos():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY,
            diagrama_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            FOREIGN KEY (diagrama_id) REFERENCES diagramas (id),
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
    ''')
    conn.commit()
    conn.close()

inicializar_banco()

criar_tabela_diagramas()
criar_tabela_produtos()
criar_tabela_pedidos()

@app.route("/api/diagramas", methods=["GET"])
def ler_diagramas():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM diagramas')
    diagramas = c.fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in diagramas])

@app.route("/api/produtos", methods=["GET"])
def ler_produtos():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM produtos')
    produtos = c.fetchall()
    conn.close()
    return jsonify(produtos)

@app.route("/api/produtos/<int:item_id>", methods=["GET"])
def obter_produto(item_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM produtos WHERE id = ?', (item_id,))
    produto = c.fetchone()
    conn.close()
    if produto is None:
        return jsonify({"erro": "Produto não encontrado"}), 404
    return jsonify(dict(produto))

@app.route("/api/produtos", methods=["POST"])
def criar_produto():
    dados = request.get_json()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO produtos (nome, preco) VALUES (?, ?)', (dados["nome"], dados["preco"]))
    conn.commit()
    conn.close()
    return jsonify({"id": c.lastrowid}), 201

@app.route("/", methods=["GET"])
def home():
    return app.send_static_file("index.html")

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(debug=False, port=porta)