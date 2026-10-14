CREATE TABLE produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT NOT NULL,
    quantidade INTEGER NOT NULL,
    preco REAL NOT NULL
);

CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produtoId INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    FOREIGN KEY (produtoId) REFERENCES produtos(id)
);

CREATE TABLE categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL
);

CREATE TABLE produtos_categorias (
    produtoId INTEGER NOT NULL,
    categoriaId INTEGER NOT NULL,
    PRIMARY KEY (produtoId, categoriaId),
    FOREIGN KEY (produtoId) REFERENCES produtos(id),
    FOREIGN KEY (categoriaId) REFERENCES categorias(id)
);

INSERT INTO categorias (nome) VALUES
('Desenho'),
('Pintura'),
('Pincéis e Ferramentas'),
('Papéis e Superfícies'),
('Kits e Acessórios'),
('Tinta'),
('Lápis'),
('Aquarela');

INSERT INTO produtos_categorias (produtoId, categoriaId) VALUES
(1, 1),
(2, 1),
(3, 2),
(4, 2),
(5, 3),
(6, 3),
(7, 3),
(8, 4),
(9, 4),
(10, 4),
(11, 5),
(12, 5),
(13, 6),
(14, 6),
(15, 7),
(16, 7),
(17, 8),
(18, 8),
(19, 9),
(20, 10);

INSERT INTO produtos (nome, descricao, quantidade, preco) VALUES
('Kit de Lápis de Cor Artísticos', 'Lápis de cor artísticos de alta qualidade', 24, 49.90),
('Kit de Lápis de Cor Profissionais', 'Lápis de cor profissionais de alta qualidade', 48, 89.90),
('Kit de Desenho com Grafite', 'Kit de desenho com lápis, borracha, apontador e esfuminho', 1, 27.90),
('Kit de Marcadores Artísticos', 'Kit de marcadores artísticos de alta qualidade', 24, 59.90),
('Canetas Fineliner', 'Conjunto de canetas fineliner de alta qualidade', 12, 32.90),
('Tinta Acrílica para Pintura', 'Tinta acrílica para pintura de alta qualidade', 12, 39.90),
('Estojo de Aquarela', 'Estojo de aquarela com pincel', 1, 44.90),
('Tinta Guache Escolar e Artística', 'Tinta guache escolar e artística de alta qualidade', 12, 24.90),
('Tinta a Óleo para Artistas', 'Tinta a óleo para artistas de alta qualidade', 6, 54.90),
('Conjunto de Pincéis Profissionais', 'Conjunto de pincéis profissionais de alta qualidade', 10, 34.90),
('Kit de Espátulas para Pintura', 'Kit de espátulas para pintura de alta qualidade', 5, 24.90),
('Paleta de Pintura Reutilizável', 'Paleta de pintura reutilizável de alta qualidade', 1, 19.90),
('Cavalete de Mesa para Pintura', 'Cavalete de mesa para pintura de alta qualidade', 1, 79.90),
('Estojo Organizador de Materiais Artísticos', 'Estojo organizador de materiais artísticos de alta qualidade', 1, 49.90),
('Kit de Lettering Criativo', 'Kit de lettering criativo com marcadores e régua', 1, 64.90),
('Kit Artista Iniciante', 'Kit artista iniciante com lápis, pincéis, tintas e bloco de desenho', 1, 99.90);

INSERT INTO pedidos (produtoId, quantidade) VALUES
(1, 1),
(2, 1),
(3, 1),
(4, 1),
(5, 1),
(6, 1),
(7, 1),
(8, 1),
(9, 1),
(10, 1),
(11, 1),
(12, 1),
(13, 1),
(14, 1),
(15, 1),
(16, 1),
(17, 1),
(18, 1),
(19, 1),
(20, 1);
