CREATE TABLE produto (
    id_produto INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    imagem TEXT,
    descricao_produto TEXT NOT NULL,
    preco_produto REAL NOT NULL,
    avaliacao_produto INTEGER NOT NULL
);

CREATE TABLE pedido (
    id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
    id_produto INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    subtotal REAL NOT NULL,
    data_pedido TEXT NOT NULL,
    FOREIGN KEY (id_produto) REFERENCES produto(id_produto)
);

CREATE TABLE favorito (
    id_favorito INTEGER PRIMARY KEY AUTOINCREMENT,
    id_produto INTEGER NOT NULL,
    data_favorito TEXT NOT NULL,
    FOREIGN KEY (id_produto) REFERENCES produto(id_produto)
);

INSERT INTO produto (nome, imagem, descricao_produto, preco_produto, avaliacao_produto)
VALUES 
    ('Café Especial Serra Clara', 'img/cafespecialserraclara.jpg', 'Café com notas de chocolate e caramelo, ideal para o dia a dia.', 34.90, 5),
    ('Café Especial Frutas Vermelhas', 'img/cafespecialfrutsvermelhas.jpg', 'Café aromático com notas frutadas e acidez delicada.', 39.90, 4.5),
    ('Café Especial Chocolate Intenso', 'img/cafespecialchocolateintenso.jpg', 'Café encorpado com notas de cacau e finalização prolongada.', 36.90, 4),
    ('Café Especial Floral', 'img/cafespecialfloral.jpg', 'Café delicado com perfil aromático floral.', 42.90, 4.8),
    ('Kit Degustação de Cafés', 'img/kitdegustacafe.jpg', 'Seleção de quatro cafés para explorar diferentes perfis de sabor.', 69.90, 4.9),
    ('Prensa Francesa', 'img/prensafrancesa.jpg', 'Método prático para preparar café encorpado em casa.', 79.90, 4.7),
    ('Coador de Cerâmica', 'img/coadoreceramica.jpg', 'Coador reutilizável com design minimalista.', 49.90, 4.6),
    ('Suporte para Coador', 'img/suportecoador.jpg', 'Suporte estável para facilitar o preparo manual.', 39.90, 4.5),
    ('Cafeteira Italiana', 'img/cafeteiraitaliana.jpg', 'Cafeteira para preparar café intenso no fogão.', 99.90, 4.4),
    ('Kit de Preparo Manual', 'img/kitdepreparomanual.jpg', 'Conjunto com coador, suporte e colher dosadora.', 119.90, 4.3),
    ('Moedor Manual de Café', 'img/moedormanualdecafe.jpg', 'Moedor compacto para moer grãos na hora.', 89.90, 4.2),
    ('Balança Digital de Precisão', 'img/balancadigitaldeprecisao.jpg', 'Balança para medir a quantidade de café e água.', 69.90, 4.1),
    ('Chaleira Bico de Ganso', 'img/chaleirabicodeganso.jpg', 'Chaleira que facilita o controle do fluxo de água.', 129.90, 4.0),
    ('Caneca de Cerâmica', 'img/canecadeceramica.jpg', 'Caneca minimalista para aproveitar sua bebida favorita.', 39.90, 4.0),
    ('Copo Térmico', 'img/copotermico.jpg', 'Copo reutilizável para manter a bebida aquecida por mais tempo.', 59.90, 4.0),
    ('Kit Café para Iniciantes', 'img/kitcafepara iniciantes.jpg', 'Conjunto com café especial, coador e caneca.', 89.90, 3.9),
    ('Kit Presente Café Especial', 'img/kitpresentecafeespecial.jpg', 'Embalagem para presente com café e acessórios selecionados.', 109.90, 3.8),
    ('Pote Hermético para Café', 'img/potehermetico para café.jpg', 'Recipiente para armazenar grãos ou café moído.', 44.90, 3.7),
    ('Colher Dosadora de Café', 'img/colherdosadora de café.jpg', 'Acessório simples para medir porções de café.', 19.90, 3.6);

INSERT INTO pedido (id_produto, quantidade, subtotal, data_pedido)
VALUES 
    (1, 2, 69.80, '2023-03-01'),
    (2, 1, 39.90, '2023-03-02'),
    (3, 3, 109.70, '2023-03-03'),
    (4, 4, 176.40, '2023-03-04'),
    (5, 2, 139.80, '2023-03-05');

INSERT INTO favorito (id_produto, data_favorito)
VALUES 
    (1, '2023-02-20'),
    (2, '2023-02-25'),
    (3, '2023-02-27'),
    (4, '2023-03-01'),
    (5, '2023-02-28');
