CREATE TABLE produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    preco REAL NOT NULL,
    descricao TEXT NOT NULL,
    imagem TEXT
);

CREATE TABLE categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT NOT NULL
);

CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data DATETIME NOT NULL,
    produto_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
);

CREATE TABLE categorias_produtos (
    produto_id INTEGER NOT NULL,
    categoria_id INTEGER NOT NULL,
    PRIMARY KEY (produto_id, categoria_id),
    FOREIGN KEY (produto_id) REFERENCES produtos(id),
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);

CREATE INDEX idx_produto_id ON pedidos (produto_id);

INSERT INTO produtos (nome, preco, descricao, imagem)
VALUES
('Chá Verde Sencha', 24.90, 'Chá verde japonês de alta qualidade', 'img/cha-verde-sencha.svg'),
('Infusão de Camomila', 19.90, 'Infusão de camomila para relaxamento', 'img/infusao-de-camomila.svg'),
('Chá Preto Earl Grey', 29.90, 'Chá preto com bergamota para um sabor cítrico', 'img/cha-preto-earl-grey.svg'),
('Blend Frutas Vermelhas', 27.90, 'Blend de chás com frutas vermelhas para um sabor doce', 'img/blend-frutas-vermelhas.svg'),
('Infusão de Hibisco e Maçã', 22.90, 'Infusão de hibisco e maçã para um sabor tropical', 'img/infusao-de-hibisco-e-maca.svg'),
('Chá Branco com Pêssego', 34.90, 'Chá branco com pêssego para um sabor cítrico', 'img/cha-branco-com-pessego.svg'),
('Blend de Hortelã e Capim-limão', 21.90, 'Blend de chás com hortelã e capim-limão', 'img/blend-de-hortela-e-capim-limao.svg'),
('Kit Degustação Aurora', 59.90, 'Kit de degustação com 4 variedades de chá', 'img/kit-degustacao-aurora.svg');

INSERT INTO categorias (nome, descricao)
VALUES
('Chá Verde', 'Chás de folhas verdes'),
('Infusão', 'Chás de folhas secas'),
('Chá Preto', 'Chás de folhas secas e caídas'),
('Blend Frutas', 'Chás com frutas'),
('Infusão de Ervas', 'Chás de ervas medicinais');

INSERT INTO pedidos (data, produto_id, quantidade)
VALUES
('2023-03-01 10:00:00', 1, 2),
('2023-03-01 11:00:00', 2, 1),
('2023-03-01 12:00:00', 3, 3),
('2023-03-01 13:00:00', 4, 2),
('2023-03-01 14:00:00', 5, 1),
('2023-03-01 15:00:00', 6, 1),
('2023-03-01 16:00:00', 7, 2),
('2023-03-01 17:00:00', 8, 1);

INSERT INTO categorias_produtos (produto_id, categoria_id)
VALUES
(1, 1),
(1, 3),
(2, 2),
(3, 1),
(3, 3),
(4, 1),
(4, 3),
(5, 2),
(6, 1),
(6, 3),
(7, 1),
(7, 3),
(8, 1);
