CREATE TABLE produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT NOT NULL,
    preco REAL NOT NULL
);

CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    preco_total REAL NOT NULL,
    FOREIGN KEY (produto_id) REFERENCES produtos (id)
);

CREATE TABLE carrinho (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    FOREIGN KEY (produto_id) REFERENCES produtos (id)
);

INSERT INTO produtos (nome, descricao, preco) VALUES
('Caderno Criativo Pastel', '100 folhas de papel de alta qualidade', 29.90),
('Planner Semanal Minimalista', 'planejamento de 12 semanas em formato A5', 39.90),
('Kit de Canetas Coloridas', '12 unidades de canetas coloridas de alta qualidade', 24.90),
('Estojo Organizador Soft', 'compartimentos internos para organizar sua papelaria', 34.90),
('Kit de Marca-Textos Pastel', '6 unidades de marcadores pastéis', 19.90),
('Bloco de Notas Adesivas', 'conjunto com 5 blocos de papel adesivo', 14.90),
('Kit de Adesivos Decorativos', '100 adesivos variados para decorar sua papelaria', 12.90),
('Agenda Permanente Floral', 'capa ilustrada e páginas organizadoras', 44.90);

INSERT INTO pedidos (produto_id, quantidade, preco_total) VALUES
(1, 1, 29.90),
(2, 1, 39.90),
(3, 2, 49.80),
(4, 1, 34.90),
(5, 1, 19.90),
(6, 1, 14.90),
(7, 1, 12.90),
(8, 1, 44.90);

INSERT INTO carrinho (produto_id, quantidade) VALUES
(1, 1),
(2, 1),
(3, 2),
(4, 1),
(5, 1),
(6, 1),
(7, 1),
(8, 1);
