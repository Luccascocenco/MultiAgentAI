CREATE TABLE produtos (
  id INTEGER PRIMARY KEY,
  nome TEXT NOT NULL,
  preco REAL NOT NULL,
  quantidade INTEGER NOT NULL,
  descricao TEXT
);

CREATE TABLE pedidos (
  id INTEGER PRIMARY KEY,
  data DATE NOT NULL,
  status TEXT NOT NULL,
  total REAL NOT NULL
);

CREATE TABLE pedidos_produtos (
  id INTEGER PRIMARY KEY,
  pedido_id INTEGER NOT NULL,
  produto_id INTEGER NOT NULL,
  quantidade INTEGER NOT NULL,
  FOREIGN KEY (pedido_id) REFERENCES pedidos (id),
  FOREIGN KEY (produto_id) REFERENCES produtos (id)
);

CREATE TABLE clientes (
  id INTEGER PRIMARY KEY,
  nome TEXT NOT NULL,
  email TEXT NOT NULL,
  telefone TEXT
);

CREATE TABLE relatorios (
  id INTEGER PRIMARY KEY,
  data DATE NOT NULL,
  tipo TEXT NOT NULL,
  conteudo TEXT
);

CREATE TABLE estoque (
  id INTEGER PRIMARY KEY,
  produto_id INTEGER NOT NULL,
  quantidade INTEGER NOT NULL,
  FOREIGN KEY (produto_id) REFERENCES produtos (id)
);

CREATE INDEX idx_produtos_nome ON produtos (nome);
CREATE INDEX idx_pedidos_data ON pedidos (data);
CREATE INDEX idx_pedidos_produtos_pedido_id ON pedidos_produtos (pedido_id);
CREATE INDEX idx_pedidos_produtos_produto_id ON pedidos_produtos (produto_id);
CREATE INDEX idx_clientes_email ON clientes (email);
CREATE INDEX idx_relatorios_data ON relatorios (data);
CREATE INDEX idx_relatorios_tipo ON relatorios (tipo);