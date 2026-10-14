CREATE TABLE produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT,
    preco REAL NOT NULL,
    imagem TEXT
);

INSERT INTO produtos (nome, descricao, preco, imagem)
VALUES
    ('Kit de Iluminação LED Automotiva', 'Iluminação branca', 89.90, 'img/kit-de-iluminacao-led-automotiva.svg'),
    ('Câmera de Ré HD', 'Visão traseira para auxiliar manobras', 129.90, 'img/camera-de-re-hd.svg'),
    ('Suporte Veicular para Celular', 'Fixação ajustável', 39.90, 'img/suporte-veicular-para-celular.svg'),
    ('Organizador de Porta-Malas', 'Compartimentos dobráveis', 69.90, 'img/organizador-de-porta-malas.svg'),
    ('Tapetes Automotivos Universais', 'Conjunto de 4 peças', 119.90, 'img/tapetes-automotivos-universais.svg'),
    ('Capa Esportiva para Volante', 'Acabamento texturizado', 49.90, 'img/capa-esportiva-para-volante.svg'),
    ('Carregador USB Automotivo', 'Duas portas de carregamento', 34.90, 'img/carregador-usb-automotivo.svg'),
    ('Aspirador Portátil para Carro', 'Limpeza interna', 99.90, 'img/aspirador-portatil-para-carro.svg');

CREATE TABLE carrinho (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
);

INSERT INTO carrinho (produto_id, quantidade)
VALUES
    (1, 1),
    (2, 1),
    (3, 1),
    (4, 1),
    (5, 1),
    (6, 1),
    (7, 1),
    (8, 1);

CREATE TABLE ordens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data DATE NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (id) REFERENCES carrinho(produto_id)
);

INSERT INTO ordens (data, status)
VALUES
    ('2023-03-01', 'Em processamento'),
    ('2023-03-02', 'Entregue'),
    ('2023-03-03', 'Cancelada');

CREATE TABLE logotipo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    imagem TEXT NOT NULL
);

INSERT INTO logotipo (imagem)
VALUES
    ('img/1.svg');

CREATE TABLE menu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    imagem TEXT
);

INSERT INTO menu (nome, imagem)
VALUES
    ('Início', 'img/inicio.svg'),
    ('Produtos', 'img/produtos.svg'),
    ('Iluminação', 'img/iluminacao.svg'),
    ('Performance', 'img/performance.svg'),
    ('Ofertas', 'img/ofertas.svg');
