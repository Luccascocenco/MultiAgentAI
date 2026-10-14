CREATE TABLE produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT NOT NULL,
    categoria TEXT NOT NULL,
    preco REAL NOT NULL,
    imagem TEXT NOT NULL
);

INSERT INTO produtos (nome, descricao, categoria, preco, imagem)
VALUES
    ('Espresso Clássico', 'Café curto e intenso, feito com grãos selecionados', 'Cafés', 6.50, 'img/espresso-classico.svg'),
    ('Cappuccino Cremoso', 'Espresso com leite vaporizado e espuma aveludada', 'Cafés', 12.00, 'img/cappuccino-cremoso.svg'),
    ('Café Coado na Hora', 'Método tradicional, aroma marcante', 'Cafés', 8.00, 'img/cafe-coado-na-hora.svg'),
    ('Latte de Caramelo', 'Leite vaporizado, espresso e calda de caramelo', 'Cafés', 14.50, 'img/latte-de-caramelo.svg'),
    ('Croissant de Manteiga', 'Folhado crocante assado todas as manhãs', 'Padaria', 9.00, 'img/croissant-de-manteiga.svg'),
    ('Pão de Queijo Mineiro', 'Porção com 4 unidades, quentinhas', 'Padaria', 10.00, 'img/pao-de-queijo-mineiro.svg'),
    ('Bolo de Cenoura com Chocolate', 'Fatia generosa com cobertura cremosa', 'Doces', 13.00, 'img/bolo-de-cenoura-com-chocolate.svg'),
    ('Torta de Limão', 'Massa amanteigada e creme leve de limão', 'Doces', 15.00, 'img/torta-de-limao.svg');

CREATE TABLE unidades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    endereco TEXT NOT NULL,
    bairro TEXT NOT NULL,
    horario TEXT NOT NULL
);

INSERT INTO unidades (nome, endereco, bairro, horario)
VALUES
    ('Unidade Centro', 'Rua das Flores, 120', 'Centro', 'Seg a Sáb, 7h às 20h'),
    ('Unidade Jardins', 'Av. das Acácias, 450', 'Jardins', 'Todos os dias, 8h às 21h'),
    ('Unidade Vila Nova', 'Rua do Comércio, 88', 'Vila Nova', 'Seg a Sex, 7h às 18h');

CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (produto_id) REFERENCES produtos (id)
);

INSERT INTO pedidos (produto_id, quantidade, status)
VALUES
    (1, 1, 'Em preparo'),
    (2, 2, 'Pronto'),
    (3, 3, 'Entregue'),
    (4, 4, 'Em preparo'),
    (5, 5, 'Pronto');

CREATE TABLE categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL
);

INSERT INTO categorias (nome)
VALUES
    ('Cafés'),
    ('Padaria'),
    ('Doces');
