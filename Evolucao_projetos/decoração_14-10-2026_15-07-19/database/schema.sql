CREATE TABLE produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    preco REAL NOT NULL,
    imagem TEXT,
    categoria TEXT NOT NULL
);

CREATE TABLE atracoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    preco REAL NOT NULL,
    imagem TEXT,
    categoria TEXT NOT NULL
);

CREATE TABLE ingressos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    preco REAL NOT NULL,
    imagem TEXT,
    categoria TEXT NOT NULL
);

CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    preco REAL NOT NULL,
    imagem TEXT,
    categoria TEXT NOT NULL
);

INSERT INTO produtos (nome, preco, imagem, categoria)
VALUES ('Vaso Decorativo Orgânico', 79.90, 'img/vaso-decorativo-organico.svg', 'Decoração'),
       ('Almofada Texturizada', 49.90, 'img/almofada-texturizada.svg', 'Decoração'),
       ('Manta para Sofá', 89.90, 'img/manta-para-sofa.svg', 'Decoração');

INSERT INTO atracoes (nome, preco, imagem, categoria)
VALUES ('Trapeza', 29.90, 'img/trapeza.svg', 'Atrações'),
       ('Elefante', 39.90, 'img/elefante.svg', 'Atrações'),
       ('Baleia', 49.90, 'img/baleia.svg', 'Atrações');

INSERT INTO ingressos (nome, preco, imagem, categoria)
VALUES ('Ingresso para Trapeza', 29.90, 'img/ingresso-para-trapeza.svg', 'Ingressos'),
       ('Ingresso para Elefante', 39.90, 'img/ingresso-para-elefante.svg', 'Ingressos'),
       ('Ingresso para Baleia', 49.90, 'img/ingresso-para-baleia.svg', 'Ingressos');

INSERT INTO pedidos (nome, preco, imagem, categoria)
VALUES ('Pedidos de produtos', 79.90, 'img/pedidos-de-produtos.svg', 'Pedidos'),
       ('Pedidos de atrações', 29.90, 'img/pedidos-de-atracoes.svg', 'Pedidos'),
       ('Pedidos de ingressos', 39.90, 'img/pedidos-de-ingressos.svg', 'Pedidos');
