CREATE TABLE diagramas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descrição TEXT NOT NULL,
    categoria TEXT NOT NULL,
    imagem TEXT
);

CREATE TABLE ingressos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    diagrama_id INTEGER NOT NULL,
    data TEXT NOT NULL,
    preco REAL NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (diagrama_id) REFERENCES diagramas(id)
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL,
    senha TEXT NOT NULL
);