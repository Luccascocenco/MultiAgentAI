CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL
);

CREATE TABLE jogos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    conteudo TEXT NOT NULL,
    preco REAL NOT NULL
);

CREATE TABLE carrinhos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    jogo_id INTEGER NOT NULL,
    quantidade REAL NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
    FOREIGN KEY (jogo_id) REFERENCES jogos (id)
);

CREATE TABLE compras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    jogo_id INTEGER NOT NULL,
    quantidade REAL NOT NULL,
    preco REAL NOT NULL,
    data DATE NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
    FOREIGN KEY (jogo_id) REFERENCES jogos (id)
);
