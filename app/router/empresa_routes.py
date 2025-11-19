from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infra.sqlalchemy.config.database import get_db
from app.schemas import schemas
from app.infra.sqlalchemy.repositorios.empresa import RepositorioEmpresa
from app.utils.jwt_bearer import get_current_user
from app.utils.role_checker import role_required


router = APIRouter(prefix="/empresas", 
                   tags=["Empresas"], 
                   dependencies=[Depends(get_current_user)]
                   )


@router.post("/", response_model=schemas.EmpresaResponse, dependencies=[Depends(role_required("adm"))], status_code=status.HTTP_201_CREATED)
def criar_empresa(empresa: schemas.EmpresaCreate, db: Session = Depends(get_db)):
    repo = RepositorioEmpresa(db)
    return repo.criar(empresa)


@router.get("/", response_model=list[schemas.EmpresaResponse], dependencies=[Depends(role_required("adm"))], status_code=status.HTTP_200_OK)
def listar_empresas(db: Session = Depends(get_db)):
    repo = RepositorioEmpresa(db)
    return repo.listar()


@router.get("/{empresa_id}", response_model=schemas.EmpresaResponse, dependencies=[Depends(role_required("adm"))], status_code=status.HTTP_200_OK)
def obter_empresa(empresa_id: int, db: Session = Depends(get_db)):
    repo = RepositorioEmpresa(db)
    empresa = repo.obter(empresa_id)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return empresa


@router.put("/{empresa_id}", response_model=schemas.EmpresaResponse, dependencies=[Depends(role_required("adm"))], status_code=status.HTTP_200_OK)
def editar_empresa(empresa_id: int, empresa: schemas.EmpresaUpdate, db: Session = Depends(get_db)):
    """Edita os dados de uma empresa pelo seu ID."""
    repo = RepositorioEmpresa(db)
    
    if not repo.obter(empresa_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada")
        
    empresa_editada = repo.editar(empresa_id, empresa)
    return empresa_editada


@router.delete("/{empresa_id}", dependencies=[Depends(role_required("adm"))], status_code=status.HTTP_200_OK)
def remover_empresa(empresa_id: int, db: Session = Depends(get_db)):
    repo = RepositorioEmpresa(db)
    sucesso = repo.remover(empresa_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return {"message": "Empresa removida com sucesso"}
