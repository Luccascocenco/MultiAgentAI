from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Conexão com o banco de dados
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Criação das tabelas
cursor.execute('''
  CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    imagem TEXT NOT NULL,
    descrição TEXT NOT NULL,
    preço REAL NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );
''')

# Insere os produtos
products = [
  ('Boneca Sofia', 'img/sofia.jpg', 'Boneca com vestido rosa e cabelos longos.', 89.90),
  ('Boneca Alice', 'img/alice.jpg', 'Boneca fashion com acessórios especiais.', 119.90),
  ('Boneca Luna', 'img/luna.jpg', 'Boneca com vestido de princesa.', 149.90),
  ('Boneca Valentina', 'img/valentina.jpg', 'Boneca ruiva com roupas modernas.', 99.90),
  ('Boneca Bella', 'img/bella.jpg', 'Boneca delicada com conjunto de acessórios.', 129.90)
]
cursor.executemany('INSERT INTO produtos VALUES (?, ?, ?, ?)', products)

# Função para devolver os produtos
def get_produtos():
  produtos = cursor.execute('SELECT * FROM produtos').fetchall()
  return produtos

# Função para devolver o carrinho
def get_carrinho():
  produtos = cursor.execute('SELECT * FROM produtos').fetchall()
  return produtos

@app.route('/api/produtos', methods=['GET'])
def produtos():
  produtos = get_produtos()
  return jsonify([dict(item) for item in produtos])

@app.route('/api/produtosCarrinho', methods=['GET'])
def carrinho():
  produtos = get_carrinho()
  return jsonify([dict(item) for item in produtos])

if __name__ == '__main__':
  app.run(debug=True)