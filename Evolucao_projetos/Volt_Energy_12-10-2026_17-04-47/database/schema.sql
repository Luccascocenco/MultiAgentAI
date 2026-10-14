CREATE TABLE produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT NOT NULL,
    preco REAL NOT NULL,
    imagem TEXT
);

INSERT INTO produtos (nome, descricao, preco, imagem)
VALUES 
('Monster Energy Original', 'Energia para o seu dia a dia', 9.99, 'img/Monster_Energy_Original.jpg'),
('Red Bull Energy Drink', 'Drinking Energy para quem não dorme', 8.49, 'img/Red_Bull_Energy_Drink.jpg'),
('Red Bull Sugarfree', 'Drinking Energy sem açúcar', 8.99, 'img/Red_Bull_Sugarfree.jpg'),
('Monster Ultra White', 'Energia para o seu coração branco', 10.99, 'img/Monster_Ultra_White.jpg'),
('TNT Energy Drink Original', 'Drinking Energy para quem não para', 7.49, 'img/TNT_Energy_Drink_Original.jpg'),
('Baly Energy Drink Tropical', 'Energia para o seu dia tropical', 6.99, 'img/Baly_Energy_Drink_Tropical.jpg'),
('Red Bull Tropical Edition', 'Drinking Energy para quem não se cala', 9.49, 'img/Red_Bull_Tropical_Edition.jpg'),
('Monster Mango Loco', 'Energia para o seu dia loco', 10.49, 'img/Monster_Mango_Loco.jpg');

CREATE TABLE carrinho (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    FOREIGN KEY (produto_id) REFERENCES produtos (id)
);

INSERT INTO carrinho (produto_id, quantidade)
VALUES 
(1, 1),
(2, 2),
(3, 1),
(4, 2),
(5, 3),
(6, 1),
(7, 2),
(8, 1);

CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (produto_id) REFERENCES produtos (id)
);

INSERT INTO pedidos (produto_id, quantidade, status)
VALUES 
(1, 1, 'em_processo'),
(2, 2, 'enviado'),
(3, 1, 'em_processo'),
(4, 2, 'enviado'),
(5, 3, 'em_processo'),
(6, 1, 'enviado'),
(7, 2, 'em_processo'),
(8, 1, 'enviado');