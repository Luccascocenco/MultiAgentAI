CREATE TABLE diagramas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT NOT NULL,
    categoria TEXT NOT NULL,
    imagem TEXT
);

CREATE TABLE ingressos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    diagrama_id INTEGER NOT NULL,
    data TEXT NOT NULL,
    preco REAL NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (diagrama_id) REFERENCES diagramas(id)
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL,
    senha TEXT NOT NULL
);

INSERT INTO diagramas (nome, descricao, categoria, imagem) 
VALUES 
('Grande Show de Acrobacias', 'Presentações aéreas e movimentos impressionantes', 'Acrobacias', 'img/acrobacias.jpg'),
('O Mundo dos Palhaços', 'Humor, brincadeiras e interação com o público', 'Palhaços', 'img/palhaços.jpg'),
('Noite de Ilusionismo', 'Truques surpreendentes e grandes ilusões', 'Ilusionismo', 'img/illusionismo.jpg'),
('Malabaristas Fantásticos', 'Equilíbrio, precisão e movimentos espetaculares', 'Malabarismo', 'img/malabarismo.jpg'),
('Aventura nas Alturas', 'Performances acrobáticas suspensas', 'Acrobacias', 'img/acrobacias-alturas.jpg'),
('O Reino da Magia', 'Personagens fantásticos e efeitos visuais encantadores', 'Magia', 'img/reino-da-magia.jpg'),
('Desafio do Equilíbrio', 'Artistas demonstrando habilidade e coordenação', 'Equilíbrio', 'img/equilíbrio.jpg'),
('O Grande Espetáculo Final', 'Presentação especial que reúne diferentes artistas e números do circo', 'Especial', 'img/grande-espetaculo-final.jpg');

INSERT INTO ingressos (diagrama_id, data, preco, status) 
VALUES 
(1, '2023-03-01', 50.00, 'Disponível'),
(2, '2023-03-02', 30.00, 'Disponível'),
(3, '2023-03-03', 40.00, 'Disponível'),
(4, '2023-03-04', 25.00, 'Disponível'),
(5, '2023-03-05', 35.00, 'Disponível'),
(6, '2023-03-06', 45.00, 'Disponível'),
(7, '2023-03-07', 50.00, 'Disponível'),
(8, '2023-03-08', 60.00, 'Disponível');

INSERT INTO users (nome, email, senha) 
VALUES 
('João', 'joao@example.com', '12345'),
('Maria', 'maria@example.com', '67890'),
('Pedro', 'pedro@example.com', '11111');
