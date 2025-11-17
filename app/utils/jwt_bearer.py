from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.utils.jwt_handler import SECRET_KEY, ALGORITHM
from app.infra.sqlalchemy.config.database import get_db
from app.infra.sqlalchemy.models import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        email: str = payload.get("email")

        if user_id is None or email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 🔑 Calcula role sempre que validar o token
        role = get_user_role(db, user_id)

        return {
            "user_id": user_id,
            "email": email,
            "role": role
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_user_role(db: Session, user_id: int) -> str:
    # Verifica se é Orientador de Gestão de Projeto (id=2)
    orientador = db.query(models.Orientador).filter(
        models.Orientador.id_usuario == user_id,
        models.Orientador.id_tipo_orientador == 2
    ).first()
    if orientador:
        return "adm"

    # Verifica se é aluno
    aluno = db.query(models.Aluno).filter(
        models.Aluno.id_usuario == user_id
    ).first()
    if aluno:
        return "aluno"

    # Default
    return "aluno"