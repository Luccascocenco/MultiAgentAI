from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

# Conexão com o banco de dados
conn = sqlite3.connect('database.db')
c = conn.cursor()

@app.route('/api/diagramas', methods=['GET'])
def carregar_diagramas():
    c.execute("SELECT * FROM diagramas")
    diagramas = c.fetchall()
    return jsonify(diagramas)

@app.route('/api/nomes', methods=['GET'])
def carregar_nomes():
    c.execute("SELECT * FROM nomes")
    nomes = c.fetchall()
    return jsonify(nomes)

@app.route('/api/conteudo', methods=['GET'])
def carregar_conteudo():
    c.execute("SELECT * FROM conteudo")
    conteudos = c.fetchall()
    return jsonify(conteudos)

@app.route('/api/relatorio', methods=['GET'])
def gerar_relatorio():
    c.execute("SELECT * FROM diagramas")
    diagramas = c.fetchall()
    c.execute("SELECT * FROM nomes")
    nomes = c.fetchall()
    c.execute("SELECT * FROM conteudo")
    conteudos = c.fetchall()
    relatorio = []
    for diagrama in diagramas:
        relatorio.append([diagrama[0], diagrama[1], diagrama[2]])
    for nome in nomes:
        relatorio.append([nome[1], nome[2], nome[0]])
    for conteudo in conteudos:
        relatorio.append([conteudo[0], conteudo[1], conteudo[2]])
    return jsonify(relatorio)

if __name__ == '__main__':
    app.run(debug=True)