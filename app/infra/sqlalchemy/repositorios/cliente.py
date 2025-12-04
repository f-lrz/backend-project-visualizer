from sqlalchemy.orm import Session
from app.schemas import schemas
from app.infra.sqlalchemy.models import models
from app.utils.security import gerar_senha, hash_senha
from sqlalchemy import func # Importe func para o tratamento de NULL no UPDATE

class RepositorioClienteRepresentante():

    def __init__(self, db: Session):
        self.db = db

    def criar(self, cliente: schemas.ClienteRepresentanteCreate):
        # 1) Cria o cliente representante (usuário)
        senha_gerada = gerar_senha(8)
        senha_hash = hash_senha(senha_gerada)

        db_usuario = models.Usuario(
            nome=cliente.nome,
            email=cliente.email,
            telefone=cliente.telefone,
            senha_hash=senha_hash
        )
        self.db.add(db_usuario)
        self.db.commit()
        self.db.refresh(db_usuario)

        # 2) Associar à empresa
        db_cliente_rep = models.Cliente_Representante(
            id_usuario=db_usuario.id_usuario,
            id_empresa=cliente.id_empresa
        )
        self.db.add(db_cliente_rep)
        self.db.commit()
        self.db.refresh(db_cliente_rep)

        print(f"Senha gerada para {db_usuario.email}: {senha_gerada}")

        return self.obter(db_usuario.id_usuario)

    def listar(self):
        """Lista todos os Clientes Representantes com seus dados de Usuário e nome da Empresa."""
        clientes = self.db.query(
            models.Usuario.id_usuario,
            models.Usuario.nome,
            models.Usuario.email,
            models.Usuario.telefone,
            models.Cliente_Representante.id_empresa,
            models.Empresa.nome.label('nome_empresa')
        ).join(models.Cliente_Representante, 
               models.Usuario.id_usuario == models.Cliente_Representante.id_usuario
        ).join(models.Empresa,
               models.Cliente_Representante.id_empresa == models.Empresa.id_empresa
        ).all()
        
        return clientes

    def obter(self, cliente_id: int):
        """Obtém um Cliente Representante pelo id_usuario, incluindo o nome da Empresa."""
        cliente = self.db.query(
            models.Usuario.id_usuario,
            models.Usuario.nome,
            models.Usuario.email,
            models.Usuario.telefone,
            models.Cliente_Representante.id_empresa,
            models.Empresa.nome.label('nome_empresa')
        ).join(models.Cliente_Representante, 
               models.Usuario.id_usuario == models.Cliente_Representante.id_usuario
        ).join(models.Empresa,
               models.Cliente_Representante.id_empresa == models.Empresa.id_empresa
        ).filter(models.Usuario.id_usuario == cliente_id)\
         .first()
        
        return cliente

    def editar(self, cliente_id: int, cliente: schemas.ClienteRepresentanteUpdate):
        """Atualiza os dados do Usuário e/ou a Empresa associada."""
        
        # 1. Atualizar dados do Usuário
        usuario_data = cliente.model_dump(exclude_unset=True, exclude={'id_empresa'})

        # Remove campos com valor None, exceto se for explicitamente desejado setar para NULL (não aplicável aqui)
        update_user_dict = {k: v for k, v in usuario_data.items() if v is not None}
        
        # Se houver dados para o Usuario, atualiza
        if update_user_dict:
            self.db.query(models.Usuario)\
                .filter(models.Usuario.id_usuario == cliente_id)\
                .update(update_user_dict)
        
        # 2. Atualizar id_empresa na tabela Cliente_Representante
        if cliente.id_empresa is not None:
            # Note: Cliente_Representante tem chave composta (id_usuario, id_empresa).
            # Para "mudar" a empresa, temos que remover o registro antigo e criar um novo.
            # No entanto, se o seu DB permite mudar PKs ou você quer apenas atualizar,
            # o jeito mais simples é atualizar o registro existente.
            
            # Buscando o registro existente para saber o id_empresa antigo
            cliente_rep = self.db.query(models.Cliente_Representante).filter(
                models.Cliente_Representante.id_usuario == cliente_id
            ).first()

            if cliente_rep:
                # Se o novo id_empresa for diferente do antigo
                if cliente_rep.id_empresa != cliente.id_empresa:
                    # Remove o registro antigo (link Cliente-Empresa)
                    self.db.delete(cliente_rep)
                    
                    # Cria o novo registro (novo link Cliente-Empresa)
                    novo_cliente_rep = models.Cliente_Representante(
                        id_usuario=cliente_id,
                        id_empresa=cliente.id_empresa
                    )
                    self.db.add(novo_cliente_rep)
            
        self.db.commit()
        return self.obter(cliente_id)

    def remover(self, cliente_id: int):
        """Remove o Cliente Representante (e o Usuário associado)."""        
        # 1. Remover da tabela Cliente_Representante (relação)
        cliente_rep = self.db.query(models.Cliente_Representante).filter(
            models.Cliente_Representante.id_usuario == cliente_id
        ).first()
        if cliente_rep:
            self.db.delete(cliente_rep)
        
        # 2. Remover da tabela Usuario
        usuario = self.db.query(models.Usuario).filter(
            models.Usuario.id_usuario == cliente_id
        ).first()

        if usuario:
            self.db.delete(usuario)
            self.db.commit()
            return True
        
        return False