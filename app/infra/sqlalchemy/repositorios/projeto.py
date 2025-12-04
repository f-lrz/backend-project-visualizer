from sqlalchemy.orm import Session, aliased
from app.schemas import schemas
from app.infra.sqlalchemy.models import models
from sqlalchemy import select, func
from datetime import datetime

class RepositorioProjeto():
    
    def __init__(self, db: Session):
        self.db = db    
       
    
    def criar_projeto_completo(self, projeto_data: schemas.ProjetoCreate):
        
        if not all(self.db.query(models.Aluno).filter(models.Aluno.id_usuario == a_id).first() for a_id in projeto_data.id_alunos_participantes):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Alguns IDs de alunos são inválidos ou não são alunos.")
        
        db_projeto = models.Projeto(
            nome=projeto_data.nome,
            descricao=projeto_data.descricao,
            data_ini=projeto_data.data_ini,
            data_fim=projeto_data.data_fim,
            status=projeto_data.status,
            id_empresa=projeto_data.id_empresa,
            nome_orientador=projeto_data.nome_orientador
        )
        self.db.add(db_projeto)
        self.db.flush()
    
        db_equipe = models.Equipe(nome=f"Equipe - {db_projeto.nome} - {datetime.now().year}")
        self.db.add(db_equipe)
        self.db.flush()
    
        now = datetime.now()
        year = now.year
        month = now.month
        semestre_atual = int(f"{year}{1 if 1 <= month <= 6 else 2}")
        
        db_equipe_projeto = models.Equipe_Projeto(
            id_equipe=db_equipe.id_equipe,
            id_projeto=db_projeto.id_projeto,
            semestre=semestre_atual,
            fase='1' # Padrão
        )
        self.db.add(db_equipe_projeto)
        
        for aluno_id in projeto_data.id_alunos_participantes:
            db_membro = models.Membro_Equipe(id_equipe=db_equipe.id_equipe, id_usuario=aluno_id)
            self.db.add(db_membro)
    
        self.db.commit()
        self.db.refresh(db_projeto)
        
        return db_projeto
    
    def listar(self):
        projetos = self.db.query(models.Projeto).all()
        return projetos
    
    def obter(self, projeto_id: int):
        return self.db.query(models.Projeto).filter(models.Projeto.id_projeto == projeto_id).first()
    
    def editar(self, projeto_id: int, projeto: schemas.ProjetoUpdate):
        update_data = projeto.model_dump(exclude_unset=True)
        
        if update_data:
            self.db.query(models.Projeto)\
                .filter(models.Projeto.id_projeto == projeto_id)\
                .update(update_data)
            self.db.commit()
            
        return self.obter(projeto_id)

    def remover(self, projeto_id: int):
        projeto = self.db.query(models.Projeto).filter(models.Projeto.id_projeto == projeto_id).first()
        if projeto:
            self.db.delete(projeto)
            self.db.commit()
            return True
        return False

    def listar_projetos_dashboard(self):
        """
        Lista todos os projetos com informações consolidadas para o dashboard.
        Busca dados do semestre ATUAL para Fase e Liderança.
        Busca Orientador Técnico (tipo_id=1) e Empresa.
        Inclui descrição, status e semestre inicial (formatado).
        """
        
        # 1. Calcula o semestre atual (YYYY1 ou YYYY2)
        now = datetime.now()
        year = now.year
        month = now.month
        semestre_atual = int(f"{year}{1 if 1 <= month <= 6 else 2}")

        # 2. Aliases para joins múltiplos na tabela Usuario
        AlunoLider = aliased(models.Usuario)

        # 4. Subquery para buscar o Aluno Líder do semestre atual
        sq_lider = select(
            models.Lideranca.id_projeto,
            AlunoLider.nome.label("aluno_lider")
        ).join(
            AlunoLider, models.Lideranca.id_usuario == AlunoLider.id_usuario
        ).filter(
            models.Lideranca.semestre == semestre_atual
        ).distinct(models.Lideranca.id_projeto).subquery()

        # 5. Subquery para buscar a Fase do semestre atual
        sq_fase = select(
            models.Equipe_Projeto.id_projeto,
            models.Equipe_Projeto.fase
        ).filter(
            models.Equipe_Projeto.semestre == semestre_atual
        ).distinct(models.Equipe_Projeto.id_projeto).subquery()

        # 6. Query Principal: Busca os dados brutos, incluindo data_ini
        query_results = self.db.query(
            models.Projeto.id_projeto,
            models.Projeto.nome.label("nome_projeto"),
            models.Projeto.descricao,
            models.Projeto.status,
            models.Projeto.data_ini,
            sq_fase.c.fase,
            models.Empresa.nome.label("empresa_demandante"),
            models.Projeto.nome_orientador.label("orientador_tecnico"),
            sq_lider.c.aluno_lider
        ).join( 
            models.Empresa, models.Projeto.id_empresa == models.Empresa.id_empresa
        ).outerjoin( 
            sq_lider, models.Projeto.id_projeto == sq_lider.c.id_projeto
        ).outerjoin( 
            sq_fase, models.Projeto.id_projeto == sq_fase.c.id_projeto
        ).distinct(models.Projeto.id_projeto).all()

        # 7. Processa os resultados para formatar a data_ini
        response_list = []
        for row in query_results:
            semestre_inicial_str = None
            if row.data_ini:
                sem = 1 if 1 <= row.data_ini.month <= 6 else 2
                semestre_inicial_str = f"{row.data_ini.year}.{sem}"
            
            response_list.append({
                "id_projeto": row.id_projeto,
                "nome_projeto": row.nome_projeto,
                "descricao": row.descricao,
                "status": row.status,
                "fase": row.fase,
                "empresa_demandante": row.empresa_demandante,
                "orientador_tecnico": row.orientador_tecnico,
                "aluno_lider": row.aluno_lider,
                "semestre_inicial": semestre_inicial_str
            })

        return response_list
    

    def get_dashboard_details(self, projeto_id: int, semestre_atual: int):
        """
        Busca os detalhes de um projeto específico para o dashboard.
        Versão simplificada: Vincula Projeto direto com Empresa.
        """

        # 3. Subquery para Fase (do semestre atual)
        sq_fase = select(
            models.Equipe_Projeto.fase
        ).filter(
            models.Equipe_Projeto.id_projeto == projeto_id,
            models.Equipe_Projeto.semestre == semestre_atual
        ).limit(1).scalar_subquery()

        # 4. Query Principal (Agora com join direto em Empresa)
        projeto = self.db.query(
            models.Projeto.id_projeto,
            models.Projeto.nome.label("nome_projeto"),
            models.Projeto.descricao,
            models.Projeto.status,
            models.Projeto.data_ini,
            models.Empresa.nome.label("empresa_demandante"),
            models.Projeto.nome_orientador.label("orientador_tecnico"),
            sq_fase.label("fase")
        ).join( # Join direto: Projeto -> Empresa
            models.Empresa, models.Projeto.id_empresa == models.Empresa.id_empresa
        ).filter(models.Projeto.id_projeto == projeto_id).first()

        if not projeto:
            return None
        
        # Formata o semestre_inicial em Python
        semestre_inicial_str = None
        if projeto.data_ini:
            sem = 1 if 1 <= projeto.data_ini.month <= 6 else 2
            semestre_inicial_str = f"{projeto.data_ini.year}.{sem}"

        # Constrói o dicionário de resposta
        response_data = {
            "id_projeto": projeto.id_projeto,
            "nome_projeto": projeto.nome_projeto,
            "descricao": projeto.descricao,
            "status": projeto.status,
            "orientador_tecnico": projeto.orientador_tecnico,
            "empresa_demandante": projeto.empresa_demandante,
            "fase": projeto.fase,
            "semestre_inicial": semestre_inicial_str
        }
        
        return response_data

    
    def get_dashboard_team(self, projeto_id: int, semestre_atual: int):
        sq_equipe_id = select(models.Equipe_Projeto.id_equipe).filter(
            models.Equipe_Projeto.id_projeto == projeto_id,
            models.Equipe_Projeto.semestre == semestre_atual
        ).limit(1).scalar_subquery()

        equipe_id = self.db.scalar(select(sq_equipe_id))

        if not equipe_id:
            return []
        
        lideres_ids = self.db.scalars(
            select(models.Lideranca.id_usuario)
            .filter(
                models.Lideranca.id_projeto == projeto_id,
                models.Lideranca.semestre == semestre_atual
            )
        ).all()

        membros_query = self.db.query(
            models.Usuario.id_usuario,
            models.Usuario.nome,
            models.Usuario.email,
            models.Usuario.telefone,
            models.Aluno.curso,
        ).join(
            models.Membro_Equipe, models.Usuario.id_usuario == models.Membro_Equipe.id_usuario
        ).outerjoin( 
            models.Aluno, models.Usuario.id_usuario == models.Aluno.id_usuario
        ).filter(
            models.Membro_Equipe.id_equipe == equipe_id
        ).all()
        
        response_list = []
        for membro in membros_query:
            response_list.append({
                "id_usuario": membro.id_usuario,
                "nome": membro.nome,
                "email": membro.email,
                "telefone": membro.telefone,
                "curso": membro.curso,
                "is_lider": (membro.id_usuario in lideres_ids)
            })
        
        return response_list