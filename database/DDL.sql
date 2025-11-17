CREATE DATABASE IF NOT EXISTS db_ttg_fstk;
USE db_ttg_fstk;

-- ================================
-- USUÁRIOS E PAPEIS
-- ================================
CREATE TABLE Usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nome       VARCHAR(100) NOT NULL,
    email      VARCHAR(100) UNIQUE NOT NULL,
    telefone   VARCHAR(20),
    senha_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Aluno (
    id_usuario INT PRIMARY KEY,
    ra         VARCHAR(20) UNIQUE NOT NULL,
    curso      VARCHAR(100),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE
);

CREATE TABLE Tipo_Orientador (
    id_tipo_orientador INT AUTO_INCREMENT PRIMARY KEY,
    nome               VARCHAR(100) NOT NULL
);

CREATE TABLE Orientador (
    id_usuario         INT,
    id_tipo_orientador INT,
    departamento       VARCHAR(100),
    PRIMARY KEY (id_usuario, id_tipo_orientador),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_tipo_orientador) REFERENCES Tipo_Orientador(id_tipo_orientador)
);

CREATE TABLE Empresa (
    id_empresa INT AUTO_INCREMENT PRIMARY KEY,
    nome       VARCHAR(100) NOT NULL,
    cnpj       VARCHAR(20) UNIQUE NOT NULL,
    descricao  TEXT
);

CREATE TABLE Cliente_Representante (
    id_usuario INT,
    id_empresa INT,
    PRIMARY KEY (id_usuario, id_empresa),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_empresa) REFERENCES Empresa(id_empresa)
);

-- ================================
-- EQUIPES E PROJETOS
-- ================================
CREATE TABLE Equipe (
    id_equipe INT AUTO_INCREMENT PRIMARY KEY,
    nome      VARCHAR(100) NOT NULL
);

CREATE TABLE Projeto (
    id_projeto INT AUTO_INCREMENT PRIMARY KEY,
    nome       VARCHAR(100) NOT NULL,
    descricao  TEXT,
    data_ini   DATE,
    data_fim   DATE,
    status     ENUM('Ativo', 'Concluído', 'Cancelado') NOT NULL,
    id_cliente_representante INT NOT NULL,
    FOREIGN KEY (id_cliente_representante) REFERENCES Usuario(id_usuario)
);

CREATE TABLE Membro_Equipe (
    id_equipe  INT,
    id_usuario INT,
    PRIMARY KEY (id_equipe, id_usuario),
    FOREIGN KEY (id_equipe) REFERENCES Equipe(id_equipe),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)
);

CREATE TABLE Equipe_Projeto (
    id_equipe  INT,
    id_projeto INT,
    semestre   INT, -- exemplo: 20211, 20212
    fase       CHAR(1), -- Fase '1' ou Fase '2'
    PRIMARY KEY (id_equipe, id_projeto, semestre),
    FOREIGN KEY (id_equipe) REFERENCES Equipe(id_equipe),
    FOREIGN KEY (id_projeto) REFERENCES Projeto(id_projeto)
);

CREATE TABLE Lideranca (
    id_projeto INT,
    id_usuario INT,
    semestre   INT, 
    PRIMARY KEY (id_projeto, id_usuario, semestre),
    FOREIGN KEY (id_projeto) REFERENCES Projeto(id_projeto),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)
);

CREATE TABLE Orientador_Projeto (
    id_projeto        INT,
    id_usuario        INT,
    id_tipo_orientador INT,
    PRIMARY KEY (id_projeto, id_usuario, id_tipo_orientador),
    FOREIGN KEY (id_projeto) REFERENCES Projeto(id_projeto),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario),
    FOREIGN KEY (id_tipo_orientador) REFERENCES Tipo_Orientador(id_tipo_orientador)
);

-- Popular dados essenciais
INSERT INTO Tipo_Orientador (nome) VALUES
('Orientador de Execução Técnica'),   -- id=1
('Orientador de Gestão de Projeto');  -- id=2