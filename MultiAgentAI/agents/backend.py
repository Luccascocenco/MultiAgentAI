from ollama import chat
import time


def backend(architecture, schema_sql=""):

    print("\n>>> BACKEND: iniciando...")

    inicio = time.time()

    # Se o agente de banco de dados já rodou, mandamos o esquema dele para
    # o back-end usar exatamente as mesmas tabelas e colunas.
    conteudo_usuario = architecture

    if schema_sql.strip():
        conteudo_usuario = (
            f"{architecture}\n\n"
            "ESQUEMA DO BANCO DE DADOS. Este é o conteúdo do arquivo "
            "database/schema.sql, que já está pronto e será lido pelo "
            "backend.py. Use EXATAMENTE estes nomes de tabelas e colunas "
            "nas rotas e nos comandos SQL, e crie rotas /api/<nome_da_tabela> "
            "para as tabelas principais:\n\n"
            f"{schema_sql}"
        )

    response = chat(

        model="llama3.2",

        messages=[

            {

                "role":"system",

                "content":
                """
                Você é um Engenheiro Back-End especializado em Python e Flask.

                REGRAS OBRIGATÓRIAS:

                - Gere APENAS UM arquivo: backend.py
                - SEMPRE use Python com Flask.
                - SEMPRE use SQLite (biblioteca sqlite3, já embutida no
                  Python — não peça para instalar nada além do Flask).
                - O banco de dados já foi definido pelo agente de banco de
                  dados e está no arquivo "database/schema.sql" (o conteúdo
                  dele vem na mensagem como ESQUEMA DO BANCO DE DADOS).
                  NÃO escreva CREATE TABLE nem INSERT dentro do Python para
                  criar o banco. Em vez disso, o backend.py deve, ao
                  iniciar, criar o arquivo "database.db" (na mesma pasta do
                  backend.py) lendo "database/schema.sql" e executando o
                  conteúdo com conn.executescript(...), apenas se o
                  database.db ainda não existir.
                - Use EXATAMENTE os nomes de tabelas e colunas do esquema.
                  Não invente colunas nem renomeie nada.
                - Pense no sistema como um CRUD completo, mas não gere front-end nem banco de dados, apenas o back-end.
                - Importe SEMPRE tudo que usar:
                  "from flask import Flask, jsonify, request".
                - Para cada tabela principal do esquema (ignore tabelas que
                  só ligam duas outras), crie 3 rotas, usando o nome da
                  tabela em minúsculas na URL:
                  GET  "/api/<tabela>"          lista todos os registros;
                  GET  "/api/<tabela>/<int:item_id>"  um registro (404 se
                       não existir);
                  POST "/api/<tabela>"          cria um registro com os
                       dados JSON recebidos (todas as colunas, menos "id").
                  Todas devolvem JSON via jsonify.
                - Em tabelas de usuários, NUNCA devolva a coluna de senha
                  (password/senha) nas respostas: liste as colunas
                  explicitamente no SELECT, sem a senha.
                - O Flask deve servir os arquivos do front-end através de
                  static_folder="static" e static_url_path="", com uma
                  rota "/" que devolve o "index.html" via
                  app.send_static_file("index.html").
                - Não faça Front-End (HTML/CSS/JS) além do necessário
                  para servir os arquivos estáticos.
                - Ao final, use exatamente este bloco para iniciar o
                  servidor (a porta vem da variável de ambiente PORT):
                      if __name__ == "__main__":
                          inicializar_banco()
                          porta = int(os.environ.get("PORT", 5000))
                          app.run(debug=False, port=porta)
                - NUNCA execute comandos externos: não use subprocess,
                  os.system, os.popen, npm, node, pip nem "pip install",
                  e NUNCA chame o programa "sqlite3" da linha de comando
                  (ele não existe no computador do usuário). O backend.py
                  só pode usar Flask e a biblioteca padrão do Python (os,
                  sqlite3, json...). Para criar o banco use SOMENTE
                  conn.executescript(...) com o texto do schema.sql.
                - O exemplo abaixo usa a tabela "produtos" apenas como
                  ilustração. NÃO crie nem use "produtos", "pedidos" ou
                  qualquer tabela que não esteja no ESQUEMA DO BANCO DE
                  DADOS recebido.
                - Antes de devolver com jsonify, converta cada linha do
                  banco com dict(linha) (nunca passe as linhas cruas).
                - Gere o arquivo UMA ÚNICA VEZ. Não repita o mesmo
                  arquivo duas vezes.
                - Não escreva nada fora do bloco de código (nem antes,
                  nem depois).
                - SEMPRE feche o bloco de código com crase tripla (```)
                  ao final.

                FORMATO OBRIGATÓRIO (siga exatamente este exemplo,
                adaptando as tabelas, colunas e rotas para o esquema
                recebido e repetindo as 3 rotas para cada tabela
                principal, mas mantendo a mesma estrutura geral):

                FILE: backend.py
                ```python
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
                    # Cria o banco a partir do schema.sql, só na primeira vez
                    if os.path.exists(DB_PATH) and os.path.getsize(DB_PATH) > 0:
                        return

                    conn = get_db_connection()
                    with open(SCHEMA_PATH, encoding="utf-8") as arquivo:
                        conn.executescript(arquivo.read())
                    conn.commit()
                    conn.close()


                @app.route("/")
                def home():
                    return app.send_static_file("index.html")


                @app.route("/api/produtos", methods=["GET"])
                def listar_produtos():
                    conn = get_db_connection()
                    linhas = conn.execute("SELECT id, nome, descricao, preco FROM produtos").fetchall()
                    conn.close()
                    return jsonify([dict(linha) for linha in linhas])


                @app.route("/api/produtos/<int:item_id>", methods=["GET"])
                def obter_produto(item_id):
                    conn = get_db_connection()
                    linha = conn.execute(
                        "SELECT id, nome, descricao, preco FROM produtos WHERE id = ?",
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
                        "INSERT INTO produtos (nome, descricao, preco) VALUES (?, ?, ?)",
                        (dados["nome"], dados.get("descricao"), dados["preco"])
                    )
                    conn.commit()
                    novo_id = cursor.lastrowid
                    conn.close()
                    return jsonify({"id": novo_id}), 201


                if __name__ == "__main__":
                    inicializar_banco()
                    porta = int(os.environ.get("PORT", 5000))
                    app.run(debug=False, port=porta)
                ```
                """

            },

            {

                "role":"user",
                "content":conteudo_usuario

            }

        ],

        options={
            "num_ctx": 8192
        }

    )

    fim = time.time()

    print(
        f">>> BACKEND: tempo de execução: "
        f"{fim - inicio:.2f} segundos"
    )

    return response.message.content