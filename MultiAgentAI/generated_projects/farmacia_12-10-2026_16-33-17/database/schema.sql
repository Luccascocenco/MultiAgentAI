CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL,
    data_nascimento DATE NOT NULL
);

CREATE TABLE produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    conteudo TEXT NOT NULL,
    preco REAL NOT NULL,
    quantidade INTEGER NOT NULL,
    imagem TEXT
);

CREATE TABLE compras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    data_compra DATE NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
    FOREIGN KEY (produto_id) REFERENCES produtos (id)
);

INSERT INTO usuarios (nome, email, senha, data_nascimento)
VALUES
('João', 'joao@example.com', '123456', '1990-01-01'),
('Maria', 'maria@example.com', '123456', '1991-02-02'),
('Pedro', 'pedro@example.com', '123456', '1992-03-03');

INSERT INTO produtos (nome, conteudo, preco, quantidade, imagem)
VALUES
('Remédio A', 'Descrição do remédio A', 10.99, 100, 'img/remedio_a.jpg'),
('Remédio B', 'Descrição do remédio B', 20.99, 50, 'img/remedio_b.jpg'),
('Remédio C', 'Descrição do remédio C', 30.99, 200, 'img/remedio_c.jpg');

INSERT INTO compras (usuario_id, produto_id, data_compra)
VALUES
(1, 1, '2023-03-01'),
(1, 2, '2023-03-15'),
(2, 1, '2023-03-20'),
(3, 3, '2023-03-25');
