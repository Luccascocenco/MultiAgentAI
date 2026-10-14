CREATE TABLE clientes (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT NOT NULL,
    telefone TEXT,
    mensagem TEXT
);

CREATE TABLE planos (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    preco REAL NOT NULL,
    descricao TEXT NOT NULL
);

CREATE TABLE aulas (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    preco REAL NOT NULL,
    descricao TEXT NOT NULL
);

CREATE TABLE equipamentos (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    preco REAL NOT NULL
);

CREATE TABLE treinos (
    id INTEGER PRIMARY KEY,
    data DATE NOT NULL,
    hora TIME NOT NULL,
    duracao REAL NOT NULL,
    cliente_id INTEGER,
    plano_id INTEGER,
    aula_id INTEGER,
    equipamento_id INTEGER,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (plano_id) REFERENCES planos(id),
    FOREIGN KEY (aula_id) REFERENCES aulas(id),
    FOREIGN KEY (equipamento_id) REFERENCES equipamentos(id)
);

CREATE TABLE reservas (
    id INTEGER PRIMARY KEY,
    data DATE NOT NULL,
    hora TIME NOT NULL,
    cliente_id INTEGER,
    plano_id INTEGER,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (plano_id) REFERENCES planos(id)
);

CREATE TABLE comentarios (
    id INTEGER PRIMARY KEY,
    comentario TEXT NOT NULL,
    data DATE NOT NULL,
    cliente_id INTEGER,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

CREATE INDEX idx_plano_id ON treinos(plano_id);
CREATE INDEX idx_aula_id ON treinos(aula_id);
CREATE INDEX idx_equipamento_id ON treinos(equipamento_id);
CREATE INDEX idx_cliente_id ON treinos(cliente_id);
CREATE INDEX idx_reserva_id ON reservas(reserva_id);
CREATE INDEX idx_comentario_id ON comentarios(comentario_id);