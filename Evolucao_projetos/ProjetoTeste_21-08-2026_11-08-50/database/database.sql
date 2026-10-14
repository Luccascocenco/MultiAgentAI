CREATE TABLE produtos (
    id INT PRIMARY KEY,
    titulo TEXT NOT NULL,
    autor TEXT NOT NULL,
    categoria TEXT NOT NULL,
    tipo VARCHAR(10) NOT NULL,
    preco DECIMAL(10, 2) NOT NULL,
    preco_promocional DECIMAL(10, 2) NOT NULL,
    quantidade_estoque INT,
    formato_ebook TEXT,
    numero_pginas INT,
    idioma TEXT,
    editora TEXT,
    ano_publicacao INT,
    avaliacao DECIMAL(3, 1) NOT NULL,
    quantidade_avalies INT NOT NULL,
    status TEXT NOT NULL,
    data_cadastro DATE NOT NULL,
    url_capa TEXT,
    palavras_chave TEXT
);

CREATE TABLE pedidos (
    id INT PRIMARY KEY,
    id_cliente INT NOT NULL,
    idProduto INT NOT NULL,
    quantidade INT NOT NULL,
    data_pedido DATE NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id),
    FOREIGN KEY (idProduto) REFERENCES produtos(id)
);

CREATE TABLE promocoes (
    id INT PRIMARY KEY,
    idProduto INT NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    desconto DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (idProduto) REFERENCES produtos(id)
);

CREATE TABLE avaliacao (
    id INT PRIMARY KEY,
    idProduto INT NOT NULL,
    id_cliente INT NOT NULL,
    avaliacao DECIMAL(3, 1) NOT NULL,
    comentario TEXT,
    data DATE NOT NULL,
    FOREIGN KEY (idProduto) REFERENCES produtos(id),
    FOREIGN KEY (id_cliente) REFERENCES clientes(id)
);

CREATE TABLE clientes (
    id INT PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT NOT NULL
);