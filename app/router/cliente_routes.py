from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import schemas
from app.infra.sqlalchemy.config.database import get_db
from app.infra.sqlalchemy.repositorios.cliente import RepositorioClienteRepresentante
from app.utils.jwt_bearer import get_current_user
from app.utils.role_checker import role_required


router = APIRouter(prefix="/clientes",
                   tags=["Clientes Representantes"],
                   dependencies=[Depends(get_current_user)]
                   )


@router.post("/", response_model=schemas.ClienteRepresentanteResponse, dependencies=[Depends(role_required("adm"))], status_code=status.HTTP_201_CREATED)
def criar_cliente(cliente: schemas.ClienteRepresentanteCreate, db: Session = Depends(get_db)):
    repo = RepositorioClienteRepresentante(db)
    # Lógica de validação de email/telefone/etc.
    return repo.criar(cliente)


@router.get("/", response_model=list[schemas.ClienteRepresentanteResponse], dependencies=[Depends(role_required("adm"))], status_code=status.HTTP_200_OK)
def listar_clientes(db: Session = Depends(get_db)):
    """Lista todos os Clientes Representantes."""
    repo = RepositorioClienteRepresentante(db)
    return repo.listar()


@router.get("/{cliente_id}", response_model=schemas.ClienteRepresentanteResponse, dependencies=[Depends(role_required("adm"))], status_code=status.HTTP_200_OK)
def obter_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Obtém um Cliente Representante pelo ID do Usuário."""
    repo = RepositorioClienteRepresentante(db)
    cliente = repo.obter(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente Representante não encontrado")
    return cliente


@router.put("/{cliente_id}", response_model=schemas.ClienteRepresentanteResponse, dependencies=[Depends(role_required("adm"))], status_code=status.HTTP_200_OK)
def editar_cliente(cliente_id: int, cliente: schemas.ClienteRepresentanteUpdate, db: Session = Depends(get_db)):
    """Edita os dados de um Cliente Representante pelo ID do Usuário."""
    repo = RepositorioClienteRepresentante(db)
    
    # Verifica se o cliente existe antes de tentar editar
    if not repo.obter(cliente_id):
        raise HTTPException(status_code=404, detail="Cliente Representante não encontrado")
        
    cliente_editado = repo.editar(cliente_id, cliente)
    return cliente_editado


@router.delete("/{cliente_id}", dependencies=[Depends(role_required("adm"))], status_code=status.HTTP_204_NO_CONTENT)
def remover_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Remove um Cliente Representante pelo ID do Usuário."""
    repo = RepositorioClienteRepresentante(db)
    sucesso = repo.remover(cliente_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Cliente Representante não encontrado")
    return # Retorna 204 No Content