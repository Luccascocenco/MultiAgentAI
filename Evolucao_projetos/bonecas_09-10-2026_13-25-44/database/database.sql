CREATE TABLE produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    imagem TEXT NOT NULL,
    descrição TEXT NOT NULL,
    preço REAL NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_nome ON produtos (nome);
CREATE INDEX idx_imagem ON produtos (imagem);
CREATE INDEX idx_descrição ON produtos (descrição);
CREATE INDEX idx_preço ON produtos (preço);

INSERT INTO produtos (nome, imagem, descrição, preço) VALUES
    ('Boneca Sofia', 'img/sofia.jpg', 'Boneca com vestido rosa e cabelos longos.', 89.90),
    ('Boneca Alice', 'img/alice.jpg', 'Boneca fashion com acessórios especiais.', 119.90),
    ('Boneca Luna', 'img/luna.jpg', 'Boneca com vestido de princesa.', 149.90),
    ('Boneca Valentina', 'img/valentina.jpg', 'Boneca ruiva com roupas modernas.', 99.90),
    ('Boneca Bella', 'img/bella.jpg', 'Boneca delicada com conjunto de acessórios.', 129.90);

INSERT INTO produtos (nome, imagem, descrição, preço) VALUES
    ('Boneta Rosa', 'img/rosa.jpg', 'Boneta rosa com saia curta e top com estampa.', 69.90),
    ('Boneca Branca', 'img/branca.jpg', 'Boneca branca com vestido de sol e sandália.', 79.90),
    ('Boneca Prazer', 'img/prazer.jpg', 'Boneca com vestido de festa e biquíni.', 89.90),
    ('Boneca Rara', 'img/rara.jpg', 'Boneca com vestido de festa e sapato alto.', 99.90),
    ('Boneca Sombra', 'img/sombra.jpg', 'Boneca com vestido de sombra e maquiagem.', 109.90);

INSERT INTO produtos (nome, imagem, descrição, preço) VALUES
    ('Boneca Dourada', 'img/dourada.jpg', 'Boneca com vestido de festa e brincadeira.', 129.90),
    ('Boneca Rosa', 'img/rosa2.jpg', 'Boneca com vestido de rosa e cabelos longos.', 99.90),
    ('Boneca Branca', 'img/branca2.jpg', 'Boneca branca com vestido de sol e sandália.', 79.90),
    ('Boneca Prazer', 'img/prazer2.jpg', 'Boneca com vestido de festa e biquíni.', 89.90),
    ('Boneca Rara', 'img/rara2.jpg', 'Boneca com vestido de festa e sapato alto.', 99.90);