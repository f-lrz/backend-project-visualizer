from sqlalchemy.orm import Session
from app.schemas import schemas
from app.infra.sqlalchemy.models import models

class RepositorioEmpresa():
    
    def __init__(self, db: Session):
        self.db = db    
    
    def criar(self, empresa: schemas.EmpresaCreate):
        db_empresa = models.Empresa(nome=empresa.nome,
                                    cnpj=empresa.cnpj,
                                    descricao=empresa.descricao)
        
        self.db.add(db_empresa)
        self.db.commit()
        self.db.refresh(db_empresa)
        
        return db_empresa
    
    def listar(self):
        empresas = self.db.query(models.Empresa).all()
        return empresas
    
    def obter(self, empresa_id: int):
        return self.db.query(models.Empresa).filter(models.Empresa.id_empresa == empresa_id).first()
    
    
    def editar(self, empresa_id: int, empresa: schemas.EmpresaUpdate):
        """Atualiza os dados de uma empresa."""
        update_data = empresa.model_dump(exclude_unset=True)
        
        if update_data:
            self.db.query(models.Empresa)\
                .filter(models.Empresa.id_empresa == empresa_id)\
                .update(update_data)
            self.db.commit()
            
        return self.obter(empresa_id)

    def remover(self, empresa_id: int):
        empresa = self.db.query(models.Empresa).filter(models.Empresa.id_empresa == empresa_id).first()
        if empresa:
            self.db.delete(empresa)
            self.db.commit()
            return True
        return False
