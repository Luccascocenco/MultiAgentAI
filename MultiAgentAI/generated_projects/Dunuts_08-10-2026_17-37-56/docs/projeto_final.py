from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import os

class App(Flask):
    def __init__(self):
        super().__init__()
        self.db = SQLAlchemy()
        self.conn = None

    def inicializar_banco(self):
        # Cria o banco a partir do schema.sql, só na primeira vez
        if os.path.exists(self.dbPath):
            return

        conn = self.conn
        with open(self.schemaPath, encoding="utf-8") as arquivo:
            conn.executescript(arquivo.read())
        conn.commit()
        conn.close()

    def get_db_connection(self):
        # Conecta ao banco de dados
        conn = sqlite3.connect(self.dbPath)
        conn.row_factory = sqlite3.Row
        return conn

# Instancia da aplicação
app = App()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.urandom(24).hex()
app.schemaPath = os.path.join(app.config["BASE_DIR"], "database", "schema.sql")
app.dbPath = os.path.join(app.config["BASE_DIR"], "database.db")

# Roda a aplicação
if __name__ == "__main__":
    app.inicializar_banco()
    porta = int(os.environ.get("PORT", 5000))
    app.run(debug=False, port=porta)