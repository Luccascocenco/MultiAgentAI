from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__, static_folder="static", static_url_path="")

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
    preço REAL NOT NULL
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

# Fechamento da conexão
conn.commit()
conn.close()

@app.route('/')
def index():
  return 'Bem-vindo ao site Pink Dolls!'

@app.route('/api/produtos', methods=["GET"])
def listar_produtos():
  conn = get_db_connection()
  linhas = conn.execute("SELECT id, nome, imagem, descrição, preço FROM produtos").fetchall()
  conn.close()
  return jsonify([dict(linha) for linha in linhas])

@app.route('/api/produtos/<int:item_id>', methods=["GET"])
def obter_produto(item_id):
  conn = get_db_connection()
  linha = conn.execute("SELECT id, nome, imagem, descrição, preço FROM produtos WHERE id = ?", (item_id,)).fetchone()
  conn.close()
  if linha is None:
    return jsonify({"erro": "Produto não encontrado"}), 404
  return jsonify(dict(linha))

@app.route('/api/produtos', methods=["POST"])
def criar_produto():
  dados = request.get_json()
  conn = get_db_connection()
  cursor = conn.execute("INSERT INTO produtos (nome, imagem, descrição, preço) VALUES (?, ?, ?, ?)", (dados["nome"], dados.get("imagem"), dados["descrição"], dados["preço"]))
  conn.commit()
  novo_id = cursor.lastrowid
  conn.close()
  return jsonify({"id": novo_id}), 201

def get_db_connection():
  conn = sqlite3.connect('database.db')
  conn.row_factory = sqlite3.Row
  return conn

if __name__ == '__main__':
  inicializar_banco()
  porta = int(os.environ.get("PORT", 5000))
  app.run(debug=False, port=porta)