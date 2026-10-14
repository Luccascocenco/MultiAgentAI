CREATE DATABASE lojaonline;

USE lojaonline;

CREATE TABLE categorias (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL
);

CREATE TABLE livros (
    id INTEGER PRIMARY KEY,
    titulo TEXT NOT NULL,
    autor TEXT NOT NULL,
    isbn TEXT NOT NULL,
    categoria_id INTEGER NOT NULL,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);

CREATE TABLE vendedores (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT NOT NULL,
    senha TEXT NOT NULL
);

CREATE TABLE clientes (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT NOT NULL,
    senha TEXT NOT NULL
);

CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY,
    data TEXT NOT NULL,
    total REAL NOT NULL,
    status TEXT NOT NULL,
    vendedor_id INTEGER NOT NULL,
    cliente_id INTEGER NOT NULL,
    FOREIGN KEY (vendedor_id) REFERENCES vendedores(id),
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

CREATE TABLE produtos (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    descricao TEXT NOT NULL,
    preco REAL NOT NULL,
    imagem TEXT NOT NULL,
    vendedor_id INTEGER NOT NULL,
    FOREIGN KEY (vendedor_id) REFERENCES vendedores(id)
);

CREATE TABLE pedidos_itens (
    id INTEGER PRIMARY KEY,
    pedido_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
);

CREATE TABLE contas (
    id INTEGER PRIMARY KEY,
    tipo TEXT NOT NULL,
    saldo REAL NOT NULL,
    vendedor_id INTEGER NOT NULL,
    FOREIGN KEY (vendedor_id) REFERENCES vendedores(id)
);

CREATE TABLE contas_itens (
    id INTEGER PRIMARY KEY,
    conta_id INTEGER NOT NULL,
    data TEXT NOT NULL,
    tipo TEXT NOT NULL,
    valor REAL NOT NULL,
    FOREIGN KEY (conta_id) REFERENCES contas(id)
);