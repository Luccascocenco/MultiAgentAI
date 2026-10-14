CREATE TABLE produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    imagem TEXT,
    descricao TEXT,
    categoria TEXT,
    volume TEXT,
    preco REAL NOT NULL,
    quantidade INTEGER NOT NULL
);

CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    id_produto INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    data DATE NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios (id),
    FOREIGN KEY (id_produto) REFERENCES produtos (id)
);

CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL
);

CREATE TABLE carrinhos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    id_produto INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    data DATE NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios (id),
    FOREIGN KEY (id_produto) REFERENCES produtos (id)
);

INSERT INTO produtos (nome, imagem, descricao, categoria, volume, preco, quantidade)
VALUES
('Chanel No. 5 Eau de Parfum', 'img/chanel-no-5-eau-de-parfum.svg', 'Eau de Parfum de luxo e sofisticado', 'Feminino', '100ml', 899.90, 10),
('Dior Sauvage Eau de Toilette', 'img/dior-sauvage-eau-de-toilette.svg', 'Eau de Toilette fresca e energética', 'Masculino', '100ml', 749.90, 20),
('Carolina Herrera Good Girl', 'img/carolina-herrera-good-girl.svg', 'Eau de Parfum feminina e sofisticada', 'Feminino', '80ml', 699.90, 15);

INSERT INTO usuarios (email, senha)
VALUES
('usuario@example.com', 'senhasegura'),
('usuario2@example.com', 'senhasegura2');

INSERT INTO carrinhos (id_usuario, id_produto, quantidade, data)
VALUES
(1, 1, 2, '2023-03-15'),
(1, 2, 1, '2023-03-16'),
(2, 3, 1, '2023-03-17');
