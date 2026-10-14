CREATE TABLE produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT,
    preco REAL
);

CREATE TABLE plantas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT,
    preco REAL
);

CREATE TABLE vasos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    tamanho TEXT,
    preco REAL
);

CREATE TABLE compras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    planta_id INTEGER,
    vaso_id INTEGER,
    produto_id INTEGER,
    quantidade INTEGER,
    preco REAL,
    FOREIGN KEY (planta_id) REFERENCES plantas (id),
    FOREIGN KEY (vaso_id) REFERENCES vasos (id),
    FOREIGN KEY (produto_id) REFERENCES produtos (id)
);

INSERT INTO produtos (nome, descricao, preco)
VALUES ('Zamioculca', 'Planta ornamentais com folhas grandes e verdes', 99.99),
       ('Dracaena', 'Planta de interior com folhas finas e longas', 49.99),
       ('Succulenta', 'Planta de interior com folhas espessas e resistentes', 29.99),
       ('Cacto', 'Planta de interior com forma única e textura interesante', 39.99),
       ('Vaso de cerâmica', 'Vaso de cerâmica de 10 cm com fenda em cima', 19.99),
       ('Vaso de madeira', 'Vaso de madeira de 15 cm com borco em cima', 29.99),
       ('Fertilizante orgânico', 'Fertilizante orgânico para plantas', 9.99),
       ('Pente de jardim', 'Pente de jardim para plantas', 7.99),
       ('Regador de jardim', 'Regador de jardim para plantas', 12.99),
       ('Mochila de jardim', 'Mochila de jardim para plantas', 24.99),
       ('Lâmpada de jardim', 'Lâmpada de jardim para plantas', 39.99),
       ('Filtro de água', 'Filtro de água para plantas', 14.99),
       ('Substraente de jardim', 'Substraente de jardim para plantas', 19.99),
       ('Poderoso', 'Poderoso para plantas', 29.99),
       ('Fertilizante químico', 'Fertilizante químico para plantas', 49.99),
       ('Rápido', 'Rápido para plantas', 39.99),
       ('Fácil', 'Fácil para plantas', 29.99),
       ('Baixo custo', 'Baixo custo para plantas', 19.99);

INSERT INTO plantas (nome, descricao, preco)
VALUES ('Zamioculca', 'Planta ornamentais com folhas grandes e verdes', 99.99),
       ('Dracaena', 'Planta de interior com folhas finas e longas', 49.99),
       ('Succulenta', 'Planta de interior com folhas espessas e resistentes', 29.99),
       ('Cacto', 'Planta de interior com forma única e textura interesante', 39.99);

INSERT INTO vasos (tipo, tamanho, preco)
VALUES ('Vaso de cerâmica', '10 cm com fenda em cima', 19.99),
       ('Vaso de madeira', '15 cm com borco em cima', 29.99);

INSERT INTO compras (planta_id, vaso_id, produto_id, quantidade, preco)
VALUES (1, 1, 1, 1, 99.99),
       (2, 2, 2, 1, 49.99),
       (3, 3, 3, 1, 29.99),
       (1, 1, 4, 1, 19.99),
       (2, 2, 5, 1, 29.99);
