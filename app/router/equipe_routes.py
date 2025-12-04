from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infra.sqlalchemy.config.database import get_db
from app.schemas import schemas
from app.infra.sqlalchemy.repositorios.equipe import RepositorioEquipe
from app.utils.jwt_bearer import get_current_user
from app.utils.role_checker import role_required
from app.infra.sqlalchemy.models import models

router = APIRouter(
    prefix="/equipes",
    tags=["Equipes"],
    dependencies=[Depends(get_current_user), Depends(role_required("adm"))]
)


# --- Rotas para Equipe ---

@router.post("/", response_model=schemas.EquipeResponse, status_code=status.HTTP_201_CREATED)
def criar_equipe(equipe: schemas.EquipeCreate, db: Session = Depends(get_db)):
    return RepositorioEquipe(db).criar_equipe(equipe)


@router.get("/", response_model=list[schemas.EquipeResponse])
def listar_equipes(db: Session = Depends(get_db)):
    return RepositorioEquipe(db).listar_equipes()


@router.put("/{equipe_id}", response_model=schemas.EquipeResponse)
def editar_equipe(equipe_id: int, equipe: schemas.EquipeUpdate, db: Session = Depends(get_db)):
    repo = RepositorioEquipe(db)
    if not repo.obter_equipe(equipe_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Equipe não encontrada")
    return repo.editar_equipe(equipe_id, equipe)


@router.delete("/{equipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_equipe(equipe_id: int, db: Session = Depends(get_db)):
    if not RepositorioEquipe(db).remover_equipe(equipe_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Equipe não encontrada")


# --- Rotas para Membros da Equipe ---

@router.post("/membros", response_model=list[schemas.MembroEquipeResponse], status_code=status.HTTP_201_CREATED)
def adicionar_membros_equipe(membro_info: schemas.MembroEquipeCreate, db: Session = Depends(get_db)):
    repo = RepositorioEquipe(db)
    
    # Validação: Verifica se a equipe existe
    equipe_existente = db.query(models.Equipe).filter(models.Equipe.id_equipe == membro_info.id_equipe).first()
    if not equipe_existente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipe com ID {membro_info.id_equipe} não encontrada."
        )

    for usuario_id in membro_info.id_usuarios:
        # Validação: Verifica se o usuário é um aluno
        aluno_existente = db.query(models.Aluno).filter(models.Aluno.id_usuario == usuario_id).first()
        if not aluno_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"O usuário com ID {usuario_id} não é um aluno e não pode ser adicionado a uma equipe como membro."
            )
        
        # Validação: Verifica se o membro já está na equipe
        membro_existente = db.query(models.Membro_Equipe).filter_by(
            id_equipe=membro_info.id_equipe, 
            id_usuario=usuario_id
        ).first()
        if membro_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"O usuário com ID {usuario_id} já é membro da equipe com ID {membro_info.id_equipe}."
            )

    return repo.adicionar_membros(membro_info.id_equipe, membro_info.id_usuarios)


@router.get("/{equipe_id}/membros", response_model=list[schemas.MembroEquipeResponse])
def listar_membros_da_equipe(equipe_id: int, db: Session = Depends(get_db)):
    return RepositorioEquipe(db).listar_membros_por_equipe(equipe_id)


@router.delete("/{equipe_id}/membros/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_membro_da_equipe(equipe_id: int, usuario_id: int, db: Session = Depends(get_db)):
    if not RepositorioEquipe(db).remover_membro(equipe_id, usuario_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Membro não encontrado na equipe")


# --- Rotas para Relacionamentos ---

@router.post("/projetos", response_model=schemas.EquipeProjetoResponse, status_code=status.HTTP_201_CREATED)
def relacionar_equipe_projeto(equipe_projeto: schemas.EquipeProjetoCreate, db: Session = Depends(get_db)):
    return RepositorioEquipe(db).relacionar_projeto(equipe_projeto)

@router.put("/projetos/{equipe_id}/{projeto_id}", response_model=schemas.EquipeProjetoResponse)
def editar_relacionamento_equipe_projeto(equipe_id: int, projeto_id: int, equipe_projeto: schemas.EquipeProjetoUpdate, db: Session = Depends(get_db)):
    repo = RepositorioEquipe(db)
    relacionamento_editado = repo.editar_relacionamento_projeto(equipe_id, projeto_id, equipe_projeto)
    if not relacionamento_editado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relacionamento Equipe/Projeto não encontrado")
    return relacionamento_editado

@router.delete("/projetos/{equipe_id}/{projeto_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_relacionamento_equipe_projeto(equipe_id: int, projeto_id: int, db: Session = Depends(get_db)):
    if not RepositorioEquipe(db).remover_relacionamento_projeto(equipe_id, projeto_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relacionamento Equipe/Projeto não encontrado")


@router.post("/lideranca", response_model=schemas.LiderancaResponse, status_code=status.HTTP_201_CREATED)
def definir_lider_equipe(lideranca: schemas.LiderancaCreate, db: Session = Depends(get_db)):
    return RepositorioEquipe(db).definir_lider(lideranca)

@router.delete("/lideranca/{projeto_id}/{usuario_id}/{semestre}", status_code=status.HTTP_204_NO_CONTENT)
def remover_lider_de_equipe(projeto_id: int, usuario_id: int, semestre: int, db: Session = Depends(get_db)):
    if not RepositorioEquipe(db).remover_lider(projeto_id, usuario_id, semestre):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Liderança não encontrada")


@router.post("/orientadores", response_model=schemas.OrientadorProjetoResponse, status_code=status.HTTP_201_CREATED)
def adicionar_orientador_projeto(orientador: schemas.OrientadorProjetoCreate, db: Session = Depends(get_db)):
    return RepositorioEquipe(db).adicionar_orientador_projeto(orientador)

@router.delete("/orientadores/{projeto_id}/{usuario_id}/{tipo_orientador_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_orientador_de_projeto(projeto_id: int, usuario_id: int, tipo_orientador_id: int, db: Session = Depends(get_db)):
    if not RepositorioEquipe(db).remover_orientador_projeto(projeto_id, usuario_id, tipo_orientador_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orientador do projeto não encontrado")