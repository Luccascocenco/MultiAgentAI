CREATE TABLE produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    preco REAL NOT NULL,
    imagem TEXT,
    descricao TEXT NOT NULL,
    categoria TEXT NOT NULL
);

CREATE TABLE carrinho (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    FOREIGN KEY (produto_id) REFERENCES produtos (id)
);

CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente TEXT NOT NULL,
    data DATETIME NOT NULL,
    total REAL NOT NULL,
    imagem TEXT
);

INSERT INTO produtos (nome, preco, imagem, descricao, categoria)
VALUES
('Caderno Premium A5', 34.90, 'img/caderno-premium-a5.svg', 'Caderno com capa minimalista e folhas pautadas para anotações diárias.', 'Cadernos e papelaria'),
('Planner Semanal', 29.90, 'img/planner-semanal.svg', 'Planner para organizar compromissos, tarefas e objetivos da semana.', 'Papelaria'),
('Bloco de Anotações', 19.90, 'img/bloco-de-anotacoes.svg', 'Bloco compacto para registrar ideias e lembretes.', 'Cadernos e papelaria'),
('Caderno de Disco Inteligente', 49.90, 'img/caderno-de-disco-inteligente.svg', 'Caderno reposicionável para personalizar e reorganizar páginas.', 'Cadernos e papelaria'),
('Kit de Notas Adesivas', 14.90, 'img/kit-de-notas-adesivas.svg', 'Conjunto de notas coloridas para marcar páginas e organizar informações.', 'Papelaria'),
('Kit de Canetas Coloridas', 24.90, 'img/kit-de-canetas-coloridas.svg', 'Conjunto de canetas para anotações, desenhos e títulos.', 'Escrita e criatividade'),
('Marcadores em Tons Pastel', 19.90, 'img/marcadores-em-tons-pastel.svg', 'Conjunto de marcadores suaves para destacar conteúdos.', 'Escrita e criatividade'),
('Caneta Gel Premium', 12.90, 'img/caneta-gel-premium.svg', 'Caneta de escrita fluida com acabamento elegante.', 'Escrita e criatividade'),
('Kit de Lápis Grafite', 9.90, 'img/kit-de-lapis-grafite.svg', 'Conjunto de lápis para escrita, esboços e exercícios.', 'Escrita e criatividade'),
('Estojo Minimalista', 29.90, 'img/estojo-minimalista.svg', 'Estojo compacto para guardar canetas e pequenos materiais.', 'Escrita e criatividade'),
('Organizador de Mesa Modular', 49.90, 'img/organizador-de-mesa-modular.svg', 'Organizador com compartimentos para materiais de estudo.', 'Organização de mesa'),
('Suporte para Notebook', 79.90, 'img/suporte-para-notebook.svg', 'Suporte para elevar o notebook e melhorar a organização da mesa.', 'Organização de mesa'),
('Porta-Canetas Geométrico', 24.90, 'img/porta-canetas-geometrico.svg', 'Porta-canetas com design moderno e compacto.', 'Organização de mesa'),
('Bandeja Organizadora', 34.90, 'img/bandeja-organizadora.svg', 'Bandeja para organizar pequenos objetos e acessórios.', 'Organização de mesa'),
('Luminária de Mesa LED', 89.90, 'img/luminaria-de-mesa-led.svg', 'Luminária compacta para iluminar a área de estudos.', 'Organização de mesa'),
('Mochila para Estudos', 129.90, 'img/mochila-para-estudos.svg', 'Mochila com compartimentos para cadernos, materiais e notebook.', 'Acessórios'),
('Bolsa Organizadora de Cabos', 39.90, 'img/bolsa-organizadora-de-cabos.svg', 'Estojo para guardar carregadores, cabos e acessórios eletrônicos.', 'Acessórios'),
('Garrafa Reutilizável 600 ml', 44.90, 'img/garrafa-reutilizavel-600-ml.svg', 'Garrafa prática para manter água por perto durante os estudos.', 'Acessórios'),
('Kit de Organização para Estudos', 59.90, 'img/kit-de-organizacao-para-estudos.svg', 'Conjunto com planner, notas adesivas e marcadores.', 'Acessórios'),
('Kit de Papelaria Criativa', 69.90, 'img/kit-de-papelaria-criativa.svg', 'Conjunto com caderno, canetas coloridas, adesivos e estojo.', 'Acessórios');

INSERT INTO pedidos (cliente, data, total)
VALUES
('João', '2023-03-01', 100.00),
('Maria', '2023-03-15', 200.00),
('Pedro', '2023-04-01', 300.00);

UPDATE pedidos SET imagem = 'img/joao.svg' WHERE id = 1;
UPDATE pedidos SET imagem = 'img/maria.svg' WHERE id = 2;
UPDATE pedidos SET imagem = 'img/pedro.svg' WHERE id = 3;
