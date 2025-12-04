from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infra.sqlalchemy.config.database import get_db
from app.schemas import schemas
from app.infra.sqlalchemy.repositorios.projeto import RepositorioProjeto
from app.utils.jwt_bearer import get_current_user
from app.utils.role_checker import role_required
from app.infra.sqlalchemy.models import models
from datetime import datetime

def get_current_semester():
    now = datetime.now()
    year = now.year
    month = now.month
    return int(f"{year}{1 if 1 <= month <= 6 else 2}")


router = APIRouter(prefix="/projetos",
                   tags=["Projetos"],
                   dependencies=[Depends(get_current_user)])


async def check_projeto_acesso(
    projeto_id: int, 
    current_user: dict = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Dependência de segurança:
    - Permite 'adm'
    - Permite 'aluno' SOMENTE SE ele for ou já foi membro do projeto (em qualquer semestre).
    """
    if current_user.get("role") == "adm":
        return current_user

    # Se for aluno, verifica a associação (independente do semestre)
    membro = db.query(models.Membro_Equipe.id_usuario).join(
        models.Equipe_Projeto, 
        models.Membro_Equipe.id_equipe == models.Equipe_Projeto.id_equipe
    ).filter(
        models.Equipe_Projeto.id_projeto == projeto_id,
        # O filtro de semestre foi REMOVIDO daqui
        models.Membro_Equipe.id_usuario == current_user.get("user_id")
    ).first()

    if not membro:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            # Mensagem de erro atualizada
            detail="Acesso negado. Você não faz parte ou nunca fez parte deste projeto."
        )
    return current_user


@router.post("/", response_model=schemas.ProjetoResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(role_required("adm"))])
def criar_projeto(projeto: schemas.ProjetoCreate, db: Session = Depends(get_db)):
    repo = RepositorioProjeto(db)
    return repo.criar_projeto_completo(projeto)


@router.get("/", response_model=list[schemas.ProjetoResponse], status_code=status.HTTP_200_OK, dependencies=[Depends(role_required("adm"))])
def listar_projetos(db: Session = Depends(get_db)):
    repo = RepositorioProjeto(db)
    return repo.listar()


@router.get("/{projeto_id}", response_model=schemas.ProjetoResponse, status_code=status.HTTP_200_OK, dependencies=[Depends(role_required("adm"))])
def obter_projeto(projeto_id: int, db: Session = Depends(get_db)):
    repo = RepositorioProjeto(db)
    projeto = repo.obter(projeto_id)
    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return projeto


@router.put("/{projeto_id}", response_model=schemas.ProjetoResponse, status_code=status.HTTP_200_OK, dependencies=[Depends(role_required("adm"))])
def editar_projeto(projeto_id: int, projeto: schemas.ProjetoUpdate, db: Session = Depends(get_db)):
    repo = RepositorioProjeto(db)
    if not repo.obter(projeto_id):
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return repo.editar(projeto_id, projeto)


@router.delete("/{projeto_id}", dependencies=[Depends(role_required("adm"))])
def remover_projeto(projeto_id: int, db: Session = Depends(get_db)):
    repo = RepositorioProjeto(db)
    if not repo.remover(projeto_id):
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return {"mensagem": "Projeto removido com sucesso"}


@router.get("/dashboard/all",
            response_model=list[schemas.ProjetoDashboardResponse],
            status_code=status.HTTP_200_OK,
            summary="Lista projetos para o dashboard (ADM)",
            dependencies=[Depends(role_required("adm"))])
def get_projetos_dashboard(db: Session = Depends(get_db)):
    """
    Retorna uma lista de todos os projetos com informações consolidadas
    para o dashboard (Fase, Orientador Técnico, Empresa, Líder).
    A fase e o líder são baseados no semestre atual.
    
    Acesso restrito a administradores.
    """
    repo = RepositorioProjeto(db)
    return repo.listar_projetos_dashboard()

@router.get("/dashboard/{projeto_id}",
            response_model=schemas.ProjetoDashboardDetailsResponse,
            status_code=status.HTTP_200_OK,
            summary="Busca detalhes de um projeto para o dashboard",
            dependencies=[Depends(check_projeto_acesso)])

def get_projeto_dashboard_details(projeto_id: int, db: Session = Depends(get_db)):
    """
    Retorna os detalhes de um projeto específico (Orientador, Empresa, Fase).
    Acesso permitido para ADM e alunos membros do projeto.
    """
    semestre_atual = get_current_semester()
    repo = RepositorioProjeto(db)
    detalhes = repo.get_dashboard_details(projeto_id, semestre_atual)
    
    if not detalhes:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
        
    return detalhes

@router.get("/{projeto_id}/dashboard-team", response_model=list[schemas.ProjetoDashboardMemberResponse], status_code=status.HTTP_200_OK, dependencies=[Depends(check_projeto_acesso)])
def get_projeto_dashboard_team(projeto_id: int, db: Session = Depends(get_db)):
    """
    Retorna a lista de membros da equipe de um projeto no semestre atual
    (Nome, Email, Curso, Feedback, Liderança).
    Acesso permitido para ADM e alunos membros do projeto.
    """
    semestre_atual = get_current_semester()
    repo = RepositorioProjeto(db)
    equipe = repo.get_dashboard_team(projeto_id, semestre_atual)
    
    # Se o projeto existe (garantido pelo check_projeto_acesso)
    # mas a equipe ainda não foi formada, retorna uma lista vazia.
    if not equipe:
        return []
        
    return equipe