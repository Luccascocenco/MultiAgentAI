CREATE TABLE diagramas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL
);

CREATE TABLE conteudo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT,
    preco REAL
);

CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER NOT NULL,
    data_venda DATE NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id)
);

CREATE TABLE clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL
);

INSERT INTO diagramas (nome) VALUES ('Diagrama 1')
INSERT INTO diagramas (nome) VALUES ('Diagrama 2')
INSERT INTO diagramas (nome) VALUES ('Diagrama 3')

INSERT INTO conteudo (nome, descricao, preco) VALUES ('Instrumento 1', 'Descrição do instrumento 1', 500.00)
INSERT INTO conteudo (nome, descricao, preco) VALUES ('Instrumento 2', 'Descrição do instrumento 2', 800.00)
INSERT INTO conteudo (nome, descricao, preco) VALUES ('Instrumento 3', 'Descrição do instrumento 3', 300.00)

INSERT INTO clientes (nome, email) VALUES ('Cliente 1', 'cliente1@example.com')
INSERT INTO clientes (nome, email) VALUES ('Cliente 2', 'cliente2@example.com')
INSERT INTO clientes (nome, email) VALUES ('Cliente 3', 'cliente3@example.com')