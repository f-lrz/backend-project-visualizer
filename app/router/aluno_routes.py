from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.infra.sqlalchemy.config.database import get_db
from app.schemas import schemas
from app.infra.sqlalchemy.repositorios import aluno as repositorio_aluno
from app.utils.jwt_bearer import get_current_user, get_user_role

# Prefixo '/alunos'
router = APIRouter(
    prefix="/alunos",
    tags=["Alunos"]
)

@router.post("/", response_model=schemas.AlunoResponse, status_code=status.HTTP_201_CREATED)
def criar_aluno(
    aluno: schemas.AlunoCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Opcional: Verificar se quem está criando é admin/orientador
    # get_user_role(current_user, ["adm", "ot", "ogp"]) 
    
    aluno_criado = repositorio_aluno.criar_aluno(db, aluno)
    return aluno_criado

@router.get("/", response_model=List[schemas.AlunoResponse])
def listar_alunos(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Apenas logados podem ver a lista
    return repositorio_aluno.listar_alunos(db)