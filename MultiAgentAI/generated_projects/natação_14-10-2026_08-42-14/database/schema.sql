CREATE TABLE turmas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    imagem TEXT,
    descricao TEXT,
    categoria TEXT,
    preco_mensal REAL NOT NULL
);

INSERT INTO turmas (nome, imagem, descricao, categoria, preco_mensal)
VALUES
('Natação para Bebês', 'img/natacao-para-bebes.svg', 'Aula com os pais para criar confiança na água', 'Bebês', 280.00),
('Adaptação ao Meio Líquido', 'img/adaptacao-ao-meio-liquido.svg', 'Primeiros contatos com a água para crianças', 'Infantil', 260.00),
('Iniciação Infantil', 'img/iniciacao-infantil.svg', 'Aprendizado dos nados crawl e costas', 'Infantil', 250.00),
('Aperfeiçoamento Juvenil', 'img/aperfeicoamento-juvenil.svg', 'Técnica dos quatro nados para crianças e adolescentes', 'Juvenil', 270.00),
('Natação para Adultos', 'img/natacao-para-adultos.svg', 'Aprenda a nadar ou perca o medo da água', 'Adultos', 300.00),
('Hidroginástica', 'img/hidroginastica.svg', 'Exercícios de baixo impacto', 'Adultos', 240.00),
('Treino de Resistência', 'img/treino-de-resistencia.svg', 'Treino para quem quer evoluir em distância e velocidade', 'Performance', 320.00),
('Equipe de Competição', 'img/equipe-de-competicao.svg', 'Treinos diários para atletas', 'Performance', 450.00);

CREATE TABLE unidades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    endereco TEXT,
    bairro TEXT,
    horario_funcionamento TEXT
);

INSERT INTO unidades (nome, endereco, bairro, horario_funcionamento)
VALUES
('Unidade Centro', 'Rua das Palmeiras, 200', 'Centro', 'Seg a Sáb, 6h às 21h'),
('Unidade Praia Azul', 'Av. do Mar, 1500', 'Praia Azul', 'Todos os dias, 7h às 20h'),
('Unidade Parque', 'Rua dos Ipês, 75', 'Jardim do Parque', 'Seg a Sex, 6h às 22h');

CREATE TABLE matriculas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_aluno TEXT,
    turma TEXT,
    unidade TEXT,
    status TEXT DEFAULT 'Ativa'
);

INSERT INTO matriculas (nome_aluno, turma, unidade)
VALUES
('João', 'Natação para Bebês', 'Unidade Centro'),
('Maria', 'Adaptação ao Meio Líquido', 'Unidade Praia Azul'),
('Pedro', 'Iniciação Infantil', 'Unidade Parque'),
('Lucia', 'Aperfeiçoamento Juvenil', 'Unidade Centro'),
('Carlos', 'Natação para Adultos', 'Unidade Praia Azul');

CREATE INDEX idx_turmas_nome ON turmas (nome);

CREATE INDEX idx_unidades_nome ON unidades (nome);

CREATE INDEX idx_matriculas_nome ON matriculas (nome_aluno);
