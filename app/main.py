from fastapi import FastAPI
from app.infra.sqlalchemy.config.database import Base, engine
from app.router import login_route
"""
from app.router import (
    equipe_routes,
    login_route,
    empresa_routes,
    aluno_routes,
    cliente_routes,
    orientador_routes,
    projeto_routes,
    nota_routes,
    upload_routes,
    encontro_routes
)
"""
from fastapi.middleware.cors import CORSMiddleware
from app.utils.jwt_bearer import get_current_user
from fastapi import Depends

# Rodar: uvicorn app.main:app --reload

app = FastAPI(title="Meu Backend")

# CORS
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui as rotas
app.include_router(login_route.router)
#app.include_router(empresa_routes.router)
#app.include_router(aluno_routes.router)
#app.include_router(cliente_routes.router)
#app.include_router(orientador_routes.router)
#app.include_router(projeto_routes.router)
#app.include_router(equipe_routes.router)


@app.get("/")
def root():
    return {"message": "API funcionando!"}


@app.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["user_id"],
        "email": current_user["email"],
        "role": current_user["role"]
    }
