CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente TEXT NOT NULL,
    itens TEXT,
    total REAL NOT NULL
);

CREATE TABLE itens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    preco REAL NOT NULL,
    imagem TEXT
);

CREATE TABLE esmaltes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cor TEXT NOT NULL
);

INSERT INTO pedidos (cliente, itens, total)
VALUES ('Cliente 1', 'item 1: preço 1', 10.99);

INSERT INTO pedidos (cliente, itens, total)
VALUES ('Cliente 2', 'item 2: preço 2', 5.99);

INSERT INTO pedidos (cliente, itens, total)
VALUES ('Cliente 3', 'item 3: preço 3', 7.99);

INSERT INTO itens (nome, preco, imagem)
VALUES ('Item 1', 1.99, 'img/item1.jpg');

INSERT INTO itens (nome, preco, imagem)
VALUES ('Item 2', 2.99, 'img/item2.jpg');

INSERT INTO itens (nome, preco, imagem)
VALUES ('Item 3', 3.99, 'img/item3.jpg');

INSERT INTO esmaltes (nome, cor)
VALUES ('Esmalte 1', 'vermelho');

INSERT INTO esmaltes (nome, cor)
VALUES ('Esmalte 2', 'azul');

INSERT INTO esmaltes (nome, cor)
VALUES ('Esmalte 3', 'amarelo');

CREATE INDEX idx_clientes ON pedidos (cliente);

CREATE INDEX idx_itens ON pedidos (itens);

CREATE INDEX idx_nomes ON itens (nome);

CREATE INDEX idx_precos ON itens (preco);

CREATE INDEX idx_nomes_esmaltes ON esmaltes (nome);

CREATE INDEX idx_cors ON esmaltes (cor);
