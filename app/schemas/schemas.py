from pydantic import BaseModel, conint
from typing import Optional, Annotated, List
from datetime import date
from enum import Enum


## Login ##

class LoginRequest(BaseModel):
    email: str
    senha: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str


## Aluno ##

class AlunoCreate(BaseModel):
    nome: str
    email: str
    telefone: str
    ra: str
    curso: str

FeedbackType = Annotated[int, conint(ge=0, le=5)]

class AlunoResponse(BaseModel):
    id_usuario: int
    nome: str
    email: str
    telefone: str
    ra: str
    curso: str

    class Config:
        from_attributes  = True

class AlunoUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    ra: Optional[str] = None
    curso: Optional[str] = None


## Empresa ##

class EmpresaCreate(BaseModel):
    nome: str
    cnpj: str
    descricao: str

class EmpresaResponse(BaseModel):
    id_empresa: int
    nome: str
    cnpj: str
    descricao: str
    
    class Config:
        from_attributes  = True

class EmpresaUpdate(BaseModel):
    nome: Optional[str] = None
    cnpj: Optional[str] = None
    descricao: Optional[str] = None


## Cliente Representante ###

class ClienteRepresentanteCreate(BaseModel):
    nome: str
    email: str
    telefone: str
    id_empresa: int

    class Config:
        from_attributes = True

class ClienteRepresentanteResponse(BaseModel):
    id_usuario: int
    nome: str
    email: str
    telefone: str
    id_empresa: int
    nome_empresa: str

    class Config:
        from_attributes = True

class ClienteRepresentanteUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    id_empresa: Optional[int] = None


## Orientador ##

class OrientadorCreate(BaseModel):
    nome: str
    email: str
    telefone: str
    id_tipo_orientador: List[int]
    departamento: str

class OrientadorUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    id_tipo_orientador: Optional[List[int]] = None
    departamento: Optional[str] = None

class OrientadorResponse(BaseModel):
    id_usuario: int
    nome: str
    email: str
    telefone: str
    id_tipo_orientador: List[int]
    departamento: str
    tipo_orientador: List[str] 

    class Config:
        from_attributes = True


## Projeto ##

class StatusProjeto(str, Enum):
    ATIVO = 'Ativo'
    CONCLUIDO = 'Concluído'
    CANCELADO = 'Cancelado'

class ProjetoCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    data_ini: Optional[date] = None
    data_fim: Optional[date] = None
    status: StatusProjeto
    id_cliente_representante: int

class ProjetoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    data_ini: Optional[date] = None
    data_fim: Optional[date] = None
    status: Optional[StatusProjeto] = None
    id_cliente_representante: Optional[int] = None

class ProjetoResponse(BaseModel):
    id_projeto: int
    nome: str
    descricao: Optional[str] = None
    data_ini: Optional[date] = None
    data_fim: Optional[date] = None
    status: str
    id_cliente_representante: int

    class Config:
        from_attributes = True

class ProjetoDashboardResponse(BaseModel):
    id_projeto: int
    nome_projeto: str
    fase: Optional[str] = None # Fase (1 ou 2)
    empresa_demandante: Optional[str] = None
    orientador_tecnico: Optional[str] = None
    aluno_lider: Optional[str] = None
    descricao: Optional[str] = None
    status: Optional[str] = None
    semestre_inicial: Optional[str] = None # Format YYYY.S

    class Config:
        from_attributes = True

class ProjetoDashboardDetailsResponse(BaseModel):
    id_projeto: int
    nome_projeto: str
    orientador_tecnico: Optional[str] = None
    empresa_demandante: Optional[str] = None
    semestre_inicial: Optional[str] = None # Format YYYY.S
    fase: Optional[str] = None # Fase (1 or 2)
    descricao: Optional[str] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True

class ProjetoDashboardMemberResponse(BaseModel):
    id_usuario: int
    nome: str
    email: str
    telefone: Optional[str] = None
    curso: Optional[str] = None
    feedback: Optional[int] = None
    is_lider: bool = False

    class Config:
        from_attributes = True


## Equipe ##

class EquipeCreate(BaseModel):
    nome: str

class EquipeUpdate(BaseModel):
    nome: Optional[str] = None

class EquipeResponse(BaseModel):
    id_equipe: int
    nome: str

    class Config:
        from_attributes = True


## Membro Equipe ##

class MembroEquipeCreate(BaseModel):
    id_equipe: int
    id_usuarios: List[int]

class MembroEquipeResponse(BaseModel):
    id_equipe: int
    id_usuario: int

    class Config:
        from_attributes = True


## Equipe Projeto ##

class EquipeProjetoCreate(BaseModel):
    id_equipe: int
    id_projeto: int
    semestre: int
    fase: str

class EquipeProjetoUpdate(BaseModel):
    semestre: Optional[int] = None
    fase: Optional[str] = None

class EquipeProjetoResponse(BaseModel):
    id_equipe: int
    id_projeto: int
    semestre: int
    fase: str

    class Config:
        from_attributes = True


## Lideranca ##

class LiderancaCreate(BaseModel):
    id_projeto: int
    id_usuario: int
    semestre: int

class LiderancaResponse(BaseModel):
    id_projeto: int
    id_usuario: int
    semestre: int

    class Config:
        from_attributes = True


## Orientador Projeto ##

class OrientadorProjetoCreate(BaseModel):
    id_projeto: int
    id_usuario: int
    id_tipo_orientador: int

class OrientadorProjetoResponse(BaseModel):
    id_projeto: int
    id_usuario: int
    id_tipo_orientador: int

    class Config:
        from_attributes = True



## Esqueci a Senha ##

class ForgotPasswordRequest(BaseModel):
    email: str
