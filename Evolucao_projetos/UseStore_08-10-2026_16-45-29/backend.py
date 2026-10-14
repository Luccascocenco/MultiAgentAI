from flask import Flask, jsonify, send_file
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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diagramas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            nome TEXT NOT NULL,
            conteúdo TEXT NOT NULL
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM diagramas")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO diagramas (tipo, nome, conteúdo) VALUES (?, ?, ?)",
            [
                ("Fluxo de Negócios", "Exemplo de Diagrama", "Este é um exemplo de diagrama"),
                ("Estrutura de Dados", "Exemplo de Estrutura", "Este é um exemplo de estrutura de dados"),
                ("Fluxo de Processos", "Exemplo de Fluxo", "Este é um exemplo de fluxo de processos"),
            ]
        )

    conn.commit()
    conn.close()

@app.route("/")
def home():
    return app.send_static_file("index.html")

@app.route("/api/diagramas")
def listar_diagramas():
    conn = get_db_connection()
    diagramas = conn.execute("SELECT * FROM diagramas").fetchall()
    conn.close()
    return jsonify([dict(d) for d in diagramas])

@app.route("/api/diagramas/<int:id>", methods=["GET"])
def obter_diagrama(id):
    conn = get_db_connection()
    diagrama = conn.execute("SELECT * FROM diagramas WHERE id=?", (id,)).fetchone()
    conn.close()
    if diagrama:
        return jsonify(dict(diagrama))
    return jsonify({"error": "Diagrama não encontrado"}), 404

@app.route("/api/diagramas", methods=["POST"])
def criar_diagrama():
    data = request.get_json()
    nome = data["nome"]
    tipo = data["tipo"]
    conteudo = data["conteudo"]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO diagramas (nome, tipo, conteúdo) VALUES (?, ?, ?)", (nome, tipo, conteudo))
    conn.commit()
    conn.close()

    return jsonify({"id": cursor.lastrowid})

if __name__ == "__main__":
    inicializar_banco()
    app.run(debug=True, port=5000)