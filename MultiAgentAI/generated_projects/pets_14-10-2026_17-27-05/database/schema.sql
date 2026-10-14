CREATE TABLE produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    imagem TEXT,
    preco REAL NOT NULL,
    avaliacao REAL NOT NULL
);

CREATE TABLE carrinho (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_produto INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    imagem TEXT,
    FOREIGN KEY (id_produto) REFERENCES produtos (id)
);

CREATE TABLE ordens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER,
    data DATE NOT NULL,
    total REAL NOT NULL,
    status TEXT NOT NULL,
    imagem TEXT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios (id)
);

INSERT INTO produtos (nome, imagem, preco, avaliacao)
VALUES
('Cama Aconchego para Cães', 'img/cama-aconchego-para-caes.svg', 119.90, 4.5),
('Cama Nuvem para Gatos', 'img/cama-nuvem-para-gatos.svg', 89.90, 4.8),
('Manta Pet Antialérgica', 'img/manta-pet-antialergica.svg', 49.90, 4.2),
('Almofada Pet Impermeável', 'img/almofada-pet-impermeavel.svg', 69.90, 4.5),
('Bola Interativa para Cães', 'img/bola-interativa-para-caes.svg', 24.90, 4.8),
('Coleira Ajustável', 'img/coleira-ajustavel.svg', 29.90, 4.2);
