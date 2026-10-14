from flask import Flask, request, jsonify
import sqlite3
from sqlite3 import Error

app = Flask(__name__)

# Conectar ao banco de dados
def conectar_banco():
    try:
        conn = sqlite3.connect('database.db')
        return conn
    except Error as e:
        print(e)

# Criar tabela de diagramas
def criar_tabela_diagramas():
    conn = conectar_banco()
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

# Criar tabela de produtos
def criar_tabela_produtos():
    conn = conectar_banco()
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

# Criar tabela de pedidos
def criar_tabela_pedidos():
    conn = conectar_banco()
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

# Criar tabela de pedidos
criar_tabela_diagramas()
criar_tabela_produtos()
criar_tabela_pedidos()

# Ler diagramas
@app.route('/api/diagramas', methods=['GET'])
def ler_diagramas():
    conn = conectar_banco()
    c = conn.cursor()
    c.execute('SELECT * FROM diagramas')
    diagramas = c.fetchall()
    conn.close()
    return jsonify(diagramas)

# Ler produtos
@app.route('/api/produtos', methods=['GET'])
def ler_produtos():
    conn = conectar_banco()
    c = conn.cursor()
    c.execute('SELECT * FROM produtos')
    produtos = c.fetchall()
    conn.close()
    return jsonify(produtos)

# Ler produtos de um diagrama
@app.route('/api/produtos/diagrama/<int:diagrama_id>', methods=['GET'])
def ler_produtos_diagrama(diagrama_id):
    conn = conectar_banco()
    c = conn.cursor()
    c.execute('SELECT * FROM produtos WHERE diagrama_id = ?', (diagrama_id,))
    produtos = c.fetchall()
    conn.close()
    return jsonify(produtos)

# Realizar pedido
@app.route('/api/produtos/pesquisa/<string:palavra>', methods=['GET'])
def realizar_pedido(palavra):
    conn = conectar_banco()
    c = conn.cursor()
    c.execute('SELECT * FROM produtos WHERE nome LIKE ?', ('%' + palavra + '%',))
    produtos = c.fetchall()
    conn.close()
    return jsonify(produtos)

if __name__ == '__main__':
    app.run(debug=True)