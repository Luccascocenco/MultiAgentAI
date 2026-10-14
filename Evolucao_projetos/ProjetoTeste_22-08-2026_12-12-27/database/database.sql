-- Crie o banco de dados para a loja de maquiagem
CREATE DATABASE loja_de_maquiagem;

-- Se o banco de dados não existir, crie-o
CREATE DATABASE IF NOT EXISTS loja_de_maquiagem;

-- Se o banco de dados não existir, crie-o novamente
CREATE DATABASE IF NOT EXISTS loja_de_maquiagem;

-- Crie o usuário e a senha para o banco de dados
CREATE USER 'loja_de_maquiagem'@'%' IDENTIFIED BY 'senha';

-- Atribua os poderes necessários ao usuário
GRANT ALL PRIVILEGES ON loja_de_maquiagem.* TO 'loja_de_maquiagem'@'%';

-- Registre o usuário
INSERT INTO mysql.user (User) VALUES ('loja_de_maquiagem');

-- Atribua o banco de dados ao usuário
ALTER USER 'loja_de_maquiagem'@'%' IDENTIFIED BY 'senha';

-- Mude a senha do usuário
ALTER USER 'loja_de_maquiagem'@'%' IDENTIFIED BY 'nova_senha';

-- Crie a tabela de clientes
CREATE TABLE clientes (
  id INT PRIMARY KEY AUTO_INCREMENT,
  nome VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  senha VARCHAR(255) NOT NULL
);

-- Crie a tabela de produtos
CREATE TABLE produtos (
  id INT PRIMARY KEY AUTO_INCREMENT,
  nome VARCHAR(255) NOT NULL,
  preco DECIMAL(10,2) NOT NULL,
  descricao TEXT
);

-- Crie a tabela de pedidos
CREATE TABLE pedidos (
  id INT PRIMARY KEY AUTO_INCREMENT,
  cliente_id INT,
  produto_id INT,
  quantidade INT NOT NULL,
  data DATE NOT NULL,
  FOREIGN KEY (cliente_id) REFERENCES clientes(id),
  FOREIGN KEY (produto_id) REFERENCES produtos(id)
);

-- Crie a tabela de pagamentos
CREATE TABLE pagamentos (
  id INT PRIMARY KEY AUTO_INCREMENT,
  pedido_id INT,
  metodo_pago VARCHAR(255) NOT NULL,
  valor DECIMAL(10,2) NOT NULL,
  data DATE NOT NULL,
  FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
);