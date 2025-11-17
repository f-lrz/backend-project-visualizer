from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.infra.sqlalchemy.config.database import get_db
from ..schemas.schemas import LoginRequest, LoginResponse, ForgotPasswordRequest
from ..controllers.auth_controller import login_user, reset_password_and_email


router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    return login_user(db, request.email, request.senha)


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Recebe um e-mail, gera uma nova senha para o usuário correspondente
    e a envia por e-mail.
    """
    return await reset_password_and_email(db, request.email)