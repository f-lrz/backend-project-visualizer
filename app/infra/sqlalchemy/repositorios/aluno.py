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

    # 2. Cria o Usuario
    senha_padrao = "123mudar" 
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

    # 3. Cria o registro na tabela Aluno
    aluno_existente = db.query(models.Aluno).filter(models.Aluno.ra == aluno.ra).first()
    if aluno_existente:
         raise HTTPException(status_code=400, detail="RA já cadastrado.")

    db_aluno = models.Aluno(
        id_usuario=db_usuario.id_usuario,
        ra=aluno.ra,
        curso=aluno.curso
    )
    db.add(db_aluno)
    db.commit()
    db.refresh(db_aluno)

    return {
        "id_usuario": db_usuario.id_usuario,
        "nome": db_usuario.nome,
        "email": db_usuario.email,
        "telefone": db_usuario.telefone,
        "ra": db_aluno.ra,
        "curso": db_aluno.curso
    }

def listar_alunos(db: Session):
    alunos_db = db.query(models.Aluno).all()
    
    resultados = []
    for al in alunos_db:
        resultados.append({
            "id_usuario": al.usuario.id_usuario,
            "nome": al.usuario.nome,
            "email": al.usuario.email,
            "telefone": al.usuario.telefone,
            "ra": al.ra,
            "curso": al.curso
        })
        
    return resultados