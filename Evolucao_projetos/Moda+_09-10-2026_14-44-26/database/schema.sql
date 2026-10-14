CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL,
    nome TEXT NOT NULL,
    sobrenome TEXT NOT NULL
);

CREATE TABLE produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT NOT NULL,
    preco REAL NOT NULL,
    imagem TEXT NOT NULL
);

CREATE TABLE carrinho (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
);

INSERT INTO usuarios (email, senha, nome, sobrenome)
VALUES
    ('jane.doe@example.com', 'senha123', 'Jane', 'Doe'),
    ('jane2@example.com', 'senha456', 'Jane', 'Doe'),
    ('jane3@example.com', 'senha789', 'Jane', 'Doe');

INSERT INTO produtos (nome, descricao, preco, imagem)
VALUES
    ('Roupas de vestir', 'Roupas de vestir para eventos especiais', 99.99, 'img/roupas-de-vestir.jpg'),
    ('Blusas de noivo', 'Blusas de noivo para casamentos', 149.99, 'img/blusas-de-noivo.jpg'),
    ('Saías de festa', 'Saías de festa para eventos especiais', 79.99, 'img/saias-de-festa.jpg');

INSERT INTO carrinho (produto_id, quantidade)
VALUES
    (1, 1),
    (2, 1),
    (3, 1);
