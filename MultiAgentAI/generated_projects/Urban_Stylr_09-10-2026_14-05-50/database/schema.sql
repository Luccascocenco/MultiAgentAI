CREATE TABLE clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT NOT NULL,
    preco REAL NOT NULL,
    imagem TEXT
);

CREATE TABLE ordens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    produtos TEXT NOT NULL,
    preco_total REAL NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

CREATE TABLE categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL
);

CREATE TABLE produtos_categorias (
    produto_id INTEGER NOT NULL,
    categoria_id INTEGER NOT NULL,
    FOREIGN KEY (produto_id) REFERENCES produtos(id),
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);

INSERT INTO clientes (nome, email) VALUES
('João', 'joao@example.com'),
('Maria', 'maria@example.com'),
('Pedro', 'pedro@example.com');

INSERT INTO produtos (nome, descricao, preco, imagem) VALUES
('Camiseta Oversized Preta', 'Camiseta confortável, com modelagem ampla e estilo urbano.', 79.90, 'img/camiseta_oversized_preta.jpg'),
('Calça Cargo Masculina', 'Calça moderna com bolsos laterais e tecido resistente.', 149.90, 'img/calca_cargo_masculina.jpg'),
('Jaqueta Jeans Feminina', 'Jaqueta jeans versátil para compor diferentes looks.', 189.90, 'img/jaqueta_jeans_feminina.jpg'),
('Tênis Casual Branco', 'Tênis minimalista para o dia a dia.', 219.90, 'img/tênis_casual_branco.jpg'),
('Boné Urban Style', 'Boné ajustável com design moderno.', 59.90, 'img/boné_urban_style.jpg');

INSERT INTO ordens (cliente_id, produtos, preco_total) VALUES
(1, 'Camiseta Oversized Preta', 79.90),
(2, 'Calça Cargo Masculina', 149.90),
(3, 'Jaqueta Jeans Feminina', 189.90);

INSERT INTO categorias (nome) VALUES
('Moda Masculina'),
('Moda Feminina'),
('Acessórios');

INSERT INTO produtos_categorias (produto_id, categoria_id) VALUES
(1, 1),
(2, 1),
(3, 2),
(4, 2),
(5, 3);
