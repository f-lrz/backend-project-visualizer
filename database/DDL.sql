USE db_ttg_fstk;

-- =======================================================
-- 1. TABELAS DE USUÁRIOS E EMPRESAS
-- =======================================================

CREATE TABLE Usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nome       VARCHAR(255) NOT NULL,
    email      VARCHAR(255) NOT NULL UNIQUE,
    telefone   VARCHAR(20),
    senha_hash VARCHAR(255) NOT NULL
);

CREATE TABLE Empresa (
    id_empresa INT AUTO_INCREMENT PRIMARY KEY,
    nome       VARCHAR(255) NOT NULL,
    cnpj       VARCHAR(255) NOT NULL,
    descricao  VARCHAR(455) NOT NULL
);

CREATE TABLE Aluno (
    id_usuario INT PRIMARY KEY,
    ra         VARCHAR(20) NOT NULL UNIQUE,
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

CREATE TABLE Cliente_Representante (
    id_usuario INT,
    id_empresa INT,
    PRIMARY KEY (id_usuario, id_empresa),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_empresa) REFERENCES Empresa(id_empresa)
);

-- =======================================================
-- 2. TABELAS DE EQUIPES E PROJETOS
-- =======================================================

CREATE TABLE Equipe (
    id_equipe INT AUTO_INCREMENT PRIMARY KEY,
    nome      VARCHAR(100) NOT NULL
);

CREATE TABLE Projeto (
    id_projeto      INT AUTO_INCREMENT PRIMARY KEY,
    nome            VARCHAR(100) NOT NULL,
    descricao       TEXT,
    data_ini        DATE,
    data_fim        DATE,
    status          ENUM('Ativo', 'Concluído', 'Cancelado') NOT NULL,
    nome_orientador VARCHAR(255),  -- Campo novo que adicionamos
    id_empresa      INT,           -- Agora vinculado a Empresa, não mais a Cliente
    FOREIGN KEY (id_empresa) REFERENCES Empresa(id_empresa)
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
    semestre   INT, 
    fase       CHAR(1), 
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

-- Mantido pois seu models.py ainda possui essa classe
CREATE TABLE Orientador_Projeto (
    id_projeto         INT,
    id_usuario         INT,
    id_tipo_orientador INT,
    PRIMARY KEY (id_projeto, id_usuario, id_tipo_orientador),
    FOREIGN KEY (id_projeto) REFERENCES Projeto(id_projeto),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario),
    FOREIGN KEY (id_tipo_orientador) REFERENCES Tipo_Orientador(id_tipo_orientador)
);

-- =======================================================
-- 3. INSERTS INICIAIS OBRIGATÓRIOS
-- =======================================================
-- Necessário para o login funcionar corretamente (role checker)
INSERT INTO Tipo_Orientador (id_tipo_orientador, nome) VALUES 
(1, 'Orientador de Execução Técnica'),
(2, 'Orientador de Gestão de Projeto');