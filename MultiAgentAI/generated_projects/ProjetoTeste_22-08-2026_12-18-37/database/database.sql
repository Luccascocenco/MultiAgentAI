CREATE TABLE produtos (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    imagem TEXT,
    descricao TEXT,
    preco REAL NOT NULL,
    contato TEXT
);

CREATE TABLE categorias (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL
);

CREATE TABLE produto_categorias (
    produto_id INTEGER NOT NULL,
    categoria_id INTEGER NOT NULL,
    PRIMARY KEY (produto_id, categoria_id),
    FOREIGN KEY (produto_id) REFERENCES produtos(id),
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);

CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT NOT NULL,
    senha TEXT NOT NULL,
    endereço TEXT,
    telefone TEXT
);

CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    data_hora TEXT NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
);

CREATE TABLE pedidos_produtos (
    pedido_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    PRIMARY KEY (pedido_id, produto_id),
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
);

CREATE TABLE carrinhos (
    id INTEGER PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    produtos TEXT NOT NULL,
    total REAL NOT NULL,
    data_hora TEXT NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);