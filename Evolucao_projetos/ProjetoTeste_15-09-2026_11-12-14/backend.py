from flask import Flask, jsonify
import sqlite3
import os

app = Flask(__name__, static_folder="static", static_url_path="")

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_banco():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Criar tabela para produtos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            preco REAL NOT NULL
        )
    """)

    # Criar tabela para pedidos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ordens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            data_hora TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    """)

    # Criar tabela para clientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            telefone TEXT NOT NULL
        )
    """)

    # Criar tabela para relatórios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS relatorios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora TEXT NOT NULL,
            total_vendidos REAL NOT NULL,
            total_espacos REAL NOT NULL
        )
    """)

    # Insere dados de exemplo
    cursor.executemany(
        "INSERT INTO produtos (nome, descricao, preco) VALUES (?, ?, ?)",
        [
            ("Produto Exemplo 1", "Descrição do produto 1", 29.90),
            ("Produto Exemplo 2", "Descrição do produto 2", 49.90),
            ("Produto Exemplo 3", "Descrição do produto 3", 19.90),
        ]
    )

    cursor.executemany(
        "INSERT INTO ordens (cliente_id, data_hora, status) VALUES (?, ?, ?)",
        [
            (1, "2022-01-01 10:00:00", "em andamento"),
            (2, "2022-01-02 11:00:00", "entregue"),
            (3, "2022-01-03 12:00:00", "em andamento"),
        ]
    )

    cursor.executemany(
        "INSERT INTO clientes (nome, email, telefone) VALUES (?, ?, ?)",
        [
            (" Cliente 1", "cliente1@example.com", "1234567890"),
            (" Cliente 2", "cliente2@example.com", "9876543210"),
            (" Cliente 3", "cliente3@example.com", "5555555555"),
        ]
    )

    cursor.executemany(
        "INSERT INTO relatorios (data_hora, total_vendidos, total_espacos) VALUES (?, ?, ?)",
        [
            ("2022-01-01 10:00:00", 100, 50),
            ("2022-01-02 11:00:00", 200, 100),
            ("2022-01-03 12:00:00", 300, 150),
        ]
    )

    conn.commit()
    conn.close()

@app.route("/")
def home():
    return app.send_static_file("index.html")

@app.route("/api/produtos")
def listar_produtos():
    conn = get_db_connection()
    produtos = conn.execute("SELECT * FROM produtos").fetchall()
    conn.close()
    return jsonify([dict(p) for p in produtos])

@app.route("/api/clientes")
def listar_clientes():
    conn = get_db_connection()
    clientes = conn.execute("SELECT * FROM clientes").fetchall()
    conn.close()
    return jsonify([dict(c) for c in clientes])

@app.route("/api/ordens")
def listar_ordens():
    conn = get_db_connection()
    ordens = conn.execute("SELECT * FROM ordens").fetchall()
    conn.close()
    return jsonify([dict(o) for o in ordens])

@app.route("/api/relatorios")
def listar_relatorios():
    conn = get_db_connection()
    relatorios = conn.execute("SELECT * FROM relatorios").fetchall()
    conn.close()
    return jsonify([dict(r) for r in relatorios])

if __name__ == "__main__":
    inicializar_banco()
    app.run(debug=True, port=5000)