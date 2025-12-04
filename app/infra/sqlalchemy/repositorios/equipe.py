from sqlalchemy.orm import Session
from app.schemas import schemas
from app.infra.sqlalchemy.models import models


class RepositorioEquipe():

    def __init__(self, db: Session):
        self.db = db

    # --- Equipe ---
    def criar_equipe(self, equipe: schemas.EquipeCreate):
        db_equipe = models.Equipe(nome=equipe.nome)
        self.db.add(db_equipe)
        self.db.commit()
        self.db.refresh(db_equipe)
        return db_equipe

    def listar_equipes(self):
        return self.db.query(models.Equipe).all()

    def obter_equipe(self, equipe_id: int):
        return self.db.query(models.Equipe).filter(models.Equipe.id_equipe == equipe_id).first()

    def editar_equipe(self, equipe_id: int, equipe: schemas.EquipeUpdate):
        update_data = equipe.model_dump(exclude_unset=True)
        if update_data:
            self.db.query(models.Equipe).filter(
                models.Equipe.id_equipe == equipe_id).update(update_data)
            self.db.commit()
        return self.obter_equipe(equipe_id)

    def remover_equipe(self, equipe_id: int):
        equipe = self.obter_equipe(equipe_id)
        if equipe:
            self.db.delete(equipe)
            self.db.commit()
            return True
        return False

    # --- Membro Equipe ---
    def adicionar_membro(self, membro: schemas.MembroEquipeCreate):
        db_membro = models.Membro_Equipe(**membro.model_dump())
        self.db.add(db_membro)
        self.db.commit()
        self.db.refresh(db_membro)
        return db_membro

    def listar_membros_por_equipe(self, equipe_id: int):
        return self.db.query(models.Membro_Equipe).filter(models.Membro_Equipe.id_equipe == equipe_id).all()

    def remover_membro(self, id_equipe: int, id_usuario: int):
        membro = self.db.query(models.Membro_Equipe).filter_by(
            id_equipe=id_equipe, id_usuario=id_usuario).first()
        if membro:
            self.db.delete(membro)
            self.db.commit()
            return True
        return False

    # --- Equipe Projeto ---
    def relacionar_projeto(self, equipe_projeto: schemas.EquipeProjetoCreate):
        db_equipe_projeto = models.Equipe_Projeto(
            **equipe_projeto.model_dump())
        self.db.add(db_equipe_projeto)
        self.db.commit()
        self.db.refresh(db_equipe_projeto)
        return db_equipe_projeto

    def editar_relacionamento_projeto(self, id_equipe: int, id_projeto: int, equipe_projeto: schemas.EquipeProjetoUpdate):
        update_data = equipe_projeto.model_dump(exclude_unset=True)
        if update_data:
            self.db.query(models.Equipe_Projeto).filter_by(
                id_equipe=id_equipe, id_projeto=id_projeto
            ).update(update_data)
            self.db.commit()
        return self.db.query(models.Equipe_Projeto).filter_by(id_equipe=id_equipe, id_projeto=id_projeto).first()

    def remover_relacionamento_projeto(self, id_equipe: int, id_projeto: int):
        relacionamento = self.db.query(models.Equipe_Projeto).filter_by(
            id_equipe=id_equipe, id_projeto=id_projeto).first()
        if relacionamento:
            self.db.delete(relacionamento)
            self.db.commit()
            return True
        return False
    
    # --- Liderança ---
    def definir_lider(self, lideranca: schemas.LiderancaCreate):
        db_lideranca = models.Lideranca(**lideranca.model_dump())
        self.db.add(db_lideranca)
        self.db.commit()
        self.db.refresh(db_lideranca)
        return db_lideranca

    def listar_lideres_por_projeto(self, projeto_id: int):
        return self.db.query(models.Lideranca).filter(models.Lideranca.id_projeto == projeto_id).all()

    def remover_lider(self, id_projeto: int, id_usuario: int, semestre: int):
        lider = self.db.query(models.Lideranca).filter_by(
            id_projeto=id_projeto, id_usuario=id_usuario, semestre=semestre).first()
        if lider:
            self.db.delete(lider)
            self.db.commit()
            return True
        return False

    # --- Orientador Projeto ---
    def adicionar_membros(self, id_equipe: int, id_usuarios: list[int]):
        membros_adicionados = []
        for user_id in id_usuarios:
            db_membro = models.Membro_Equipe(id_equipe=id_equipe, id_usuario=user_id)
            self.db.add(db_membro)
            self.db.commit()
            self.db.refresh(db_membro)
            membros_adicionados.append(db_membro)
        return membros_adicionados

    def listar_orientadores_por_projeto(self, projeto_id: int):
        return self.db.query(models.Orientador_Projeto).filter(models.Orientador_Projeto.id_projeto == projeto_id).all()

    def remover_orientador_projeto(self, id_projeto: int, id_usuario: int, id_tipo_orientador: int):
        orientador = self.db.query(models.Orientador_Projeto).filter_by(
            id_projeto=id_projeto,
            id_usuario=id_usuario,
            id_tipo_orientador=id_tipo_orientador
        ).first()
        if orientador:
            self.db.delete(orientador)
            self.db.commit()
            return True
        return False