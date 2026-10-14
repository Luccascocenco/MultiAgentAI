CREATE TABLE diagramas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    conteúdo TEXT NOT NULL
);

CREATE TABLE nomes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    nome TEXT NOT NULL
);

CREATE TABLE conteúdo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    quantidade INTEGER NOT NULL,
    preço REAL NOT NULL
);

INSERT INTO diagramas (nome, conteúdo) VALUES ('Diagrama 1', 'Este é o conteúdo do diagrama 1');

INSERT INTO diagramas (nome, conteúdo) VALUES ('Diagrama 2', 'Este é o conteúdo do diagrama 2');

INSERT INTO diagramas (nome, conteúdo) VALUES ('Diagrama 3', 'Este é o conteúdo do diagrama 3');

INSERT INTO nomes (tipo, nome) VALUES ('Dunut', 'Pão de Açúcar');

INSERT INTO nomes (tipo, nome) VALUES ('Pão', 'Pão de Queijo');

INSERT INTO nomes (tipo, nome) VALUES ('Dunut', 'Dunut de Chocolate');

INSERT INTO conteúdo (nome, quantidade, preço) VALUES ('Pão de Açúcar', 10, 2.50);

INSERT INTO conteúdo (nome, quantidade, preço) VALUES ('Pão de Queijo', 20, 3.00);

INSERT INTO conteúdo (nome, quantidade, preço) VALUES ('Dunut de Chocolate', 30, 4.00);
