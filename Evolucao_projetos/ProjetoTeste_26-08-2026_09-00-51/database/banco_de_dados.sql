CREATE TABLE categorias (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL
);

CREATE TABLE produtos (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    preco REAL NOT NULL,
    descricao TEXT
);

CREATE TABLE quadros (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    preco REAL NOT NULL,
    descricao TEXT,
    categoria_id INTEGER,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);

CREATE TABLE carrinho (
    id INTEGER PRIMARY KEY,
    produto_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
);

CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY,
    data_hora TEXT NOT NULL,
    total REAL NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE pedidos_carrinho (
    id INTEGER PRIMARY KEY,
    pedido_id INTEGER NOT NULL,
    carrinho_id INTEGER NOT NULL,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    FOREIGN KEY (carrinho_id) REFERENCES carrinho(id)
);

CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT NOT NULL,
    senha TEXT NOT NULL
);

CREATE TABLE order_pedidos (
    id INTEGER PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    pedido_id INTEGER NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
);

CREATE TABLE comentario (
    id INTEGER PRIMARY KEY,
    produto_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    comentario TEXT NOT NULL,
    FOREIGN KEY (produto_id) REFERENCES quadros(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

CREATE INDEX idx_categorias ON categorias (nome);
CREATE INDEX idx_produtos ON produtos (nome);
CREATE INDEX idx_quadros ON quadros (nome);
CREATE INDEX idx_carrinho ON carrinho (produto_id);
CREATE INDEX idx_pedidos ON pedidos (data_hora);
CREATE INDEX idx_usuarios ON usuarios (email);