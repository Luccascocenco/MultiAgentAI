CREATE DATABASE diagrama-creator;

USE diagrama-creator;

CREATE TABLE Diagrama (
    id INTEGER PRIMARY KEY,
    tipo VARCHAR(255) NOT NULL,
    nome TEXT NOT NULL,
    conteúdo TEXT NOT NULL
);

CREATE TABLE Elemento (
    id INTEGER PRIMARY KEY,
    tipo VARCHAR(255) NOT NULL,
    nome TEXT NOT NULL,
    conteúdo TEXT NOT NULL
);

CREATE TABLE User (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    email TEXT NOT NULL
);

CREATE TABLE Collaboration (
    id INTEGER PRIMARY KEY,
    diagrama_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    FOREIGN KEY (diagrama_id) REFERENCES Diagrama(id),
    FOREIGN KEY (user_id) REFERENCES User(id)
);

CREATE INDEX idx_diagrama_id ON Collaboration(diagrama_id);
CREATE INDEX idx_user_id ON Collaboration(user_id);