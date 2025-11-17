from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Date, TEXT, CHAR, DECIMAL, Boolean
from sqlalchemy.orm import relationship
from app.infra.sqlalchemy.config.database import Base

class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    telefone = Column(String(20))
    senha_hash = Column(String(255), nullable=False)
    
    aluno = relationship("Aluno", back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    cliente_representantes = relationship("Cliente_Representante", back_populates="usuario", cascade="all, delete-orphan")
    orientadores = relationship("Orientador", back_populates="usuario", cascade="all, delete-orphan")


class Empresa(Base):
    __tablename__ = "empresa"
    
    id_empresa = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    cnpj = Column(String(255), nullable=False)
    descricao = Column(String(455), nullable=False)

    clientes_representantes = relationship("Cliente_Representante", back_populates="empresa", cascade="all, delete-orphan")

class Aluno(Base):
    __tablename__ = "aluno"

    id_usuario = Column(Integer, ForeignKey('usuario.id_usuario'), primary_key=True)
    ra = Column(String(20), unique=True, nullable=False)
    curso = Column(String(100))
    
    usuario = relationship("Usuario", back_populates="aluno")

class Projeto(Base):
    __tablename__ = "projeto"

    id_projeto = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(TEXT)
    data_ini = Column(Date)
    data_fim = Column(Date)
    status = Column(Enum('Ativo', 'Concluído', 'Cancelado'), nullable=False)
    id_cliente_representante = Column(Integer, ForeignKey("usuario.id_usuario"))

class Cliente_Representante(Base):
    __tablename__ = "cliente_representante"

    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), primary_key=True)
    id_empresa = Column(Integer, ForeignKey("empresa.id_empresa"), primary_key=True)

    usuario = relationship("Usuario", back_populates="cliente_representantes")
    empresa = relationship("Empresa", back_populates="clientes_representantes")

class Tipo_Orientador(Base):
    __tablename__ = "tipo_orientador"

    id_tipo_orientador = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)

    orientadores = relationship("Orientador", back_populates="tipo_orientador")

class Orientador(Base):
    __tablename__ = "orientador"

    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), primary_key=True)
    id_tipo_orientador = Column(Integer, ForeignKey("tipo_orientador.id_tipo_orientador"), primary_key=True)
    departamento = Column(String(100))

    usuario = relationship("Usuario", back_populates="orientadores")
    tipo_orientador = relationship("Tipo_Orientador", back_populates="orientadores")

class Equipe(Base):
    __tablename__ = "equipe"

    id_equipe = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)

class Membro_Equipe(Base):
    __tablename__ = "membro_equipe"

    id_equipe = Column(Integer, ForeignKey("equipe.id_equipe"), primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), primary_key=True)

class Equipe_Projeto(Base):
    __tablename__ = "equipe_projeto"

    id_equipe = Column(Integer, ForeignKey("equipe.id_equipe"), primary_key=True)
    id_projeto = Column(Integer, ForeignKey("projeto.id_projeto"), primary_key=True)
    semestre = Column(Integer, primary_key=True)
    fase = Column(CHAR(1))

class Lideranca(Base):
    __tablename__ = "lideranca"

    id_projeto = Column(Integer, ForeignKey("projeto.id_projeto"), primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), primary_key=True)
    semestre = Column(Integer, primary_key=True)

class Orientador_Projeto(Base):
    __tablename__ = "orientador_projeto"

    id_projeto = Column(Integer, ForeignKey("projeto.id_projeto"), primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), primary_key=True)
    id_tipo_orientador = Column(Integer, ForeignKey("tipo_orientador.id_tipo_orientador"), primary_key=True)

