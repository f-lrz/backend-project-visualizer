from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.schemas import schemas
from app.infra.sqlalchemy.models import models
from app.utils.security import hash_senha

def criar_aluno(db: Session, aluno: schemas.AlunoCreate):
    # 1. Verifica se e-mail já existe na tabela Usuario
    usuario_existente = db.query(models.Usuario).filter(models.Usuario.email == aluno.email).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado."
        )

    # 2. Cria o Usuario (com senha padrão hashada, ex: '123mudar' ou gerada)
    senha_padrao = "123mudar" # Você pode mudar lógica de senha aqui
    senha_hash = hash_senha(senha_padrao)

    db_usuario = models.Usuario(
        nome=aluno.nome,
        email=aluno.email,
        telefone=aluno.telefone,
        senha_hash=senha_hash
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)

    # 3. Cria o registro na tabela Aluno vinculado ao Usuario
    # Verifica se RA já existe
    aluno_existente = db.query(models.Aluno).filter(models.Aluno.ra == aluno.ra).first()
    if aluno_existente:
         # Rollback manual se falhar aqui é boa prática, mas para MVP ok
         raise HTTPException(status_code=400, detail="RA já cadastrado.")

    db_aluno = models.Aluno(
        id_usuario=db_usuario.id_usuario,
        ra=aluno.ra,
        curso=aluno.curso
    )
    db.add(db_aluno)
    db.commit()
    db.refresh(db_aluno)

    return db_aluno

def listar_alunos(db: Session):
    # Retorna todos os alunos (fazendo join com usuario para pegar o nome)
    return db.query(models.Aluno).all()