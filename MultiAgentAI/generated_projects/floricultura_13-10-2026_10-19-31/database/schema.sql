CREATE TABLE diagramas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    conteudo TEXT NOT NULL
);

CREATE TABLE produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT NOT NULL,
    preco REAL NOT NULL
);

CREATE TABLE compras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_produto INTEGER NOT NULL,
    data_compra DATE NOT NULL,
    quantidade INTEGER NOT NULL,
    FOREIGN KEY (id_produto) REFERENCES produtos (id)
);

CREATE TABLE imagens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    imagem TEXT NOT NULL,
    produto_id INTEGER NOT NULL,
    FOREIGN KEY (produto_id) REFERENCES produtos (id)
);

INSERT INTO diagramas (nome, conteudo) VALUES ('Diagrama 1', 'Conteúdo do diagrama 1');

INSERT INTO diagramas (nome, conteudo) VALUES ('Diagrama 2', 'Conteúdo do diagrama 2');

INSERT INTO diagramas (nome, conteudo) VALUES ('Diagrama 3', 'Conteúdo do diagrama 3');

INSERT INTO produtos (nome, descricao, preco) VALUES ('Buquê de Rosas Vermelhas', '12 rosas', 129.90);

INSERT INTO produtos (nome, descricao, preco) VALUES ('Buquê de Girassóis', '6 girassóis', 89.90);

INSERT INTO produtos (nome, descricao, preco) VALUES ('Buquê de Tulipas Coloridas', '10 tulipas', 149.90);

INSERT INTO compras (id_produto, data_compra, quantidade) VALUES (1, '2023-03-01', 1);

INSERT INTO compras (id_produto, data_compra, quantidade) VALUES (2, '2023-03-02', 2);

INSERT INTO compras (id_produto, data_compra, quantidade) VALUES (3, '2023-03-03', 3);

INSERT INTO imagens (nome, imagem, produto_id) VALUES ('imagem1.jpg', 'img/nome1.jpg', 1);

INSERT INTO imagens (nome, imagem, produto_id) VALUES ('imagem2.jpg', 'img/nome2.jpg', 2);

INSERT INTO imagens (nome, imagem, produto_id) VALUES ('imagem3.jpg', 'img/nome3.jpg', 3);
