from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.infra.sqlalchemy.models.models import Usuario
from app.utils.security import verificar_senha, gerar_senha, hash_senha
from app.utils.security import verificar_senha
from app.utils.jwt_handler import criar_access_token
from app.infra.sqlalchemy.models import models
from app.utils.email_handler import send_email


def login_user(db: Session, email: str, senha: str):
    user = db.query(Usuario).filter(Usuario.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if not verificar_senha(senha, user.senha_hash):
        raise HTTPException(status_code=401, detail="Senha incorreta")

    access_token = criar_access_token({
        "user_id": user.id_usuario,
        "email": user.email
    })

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

async def reset_password_and_email(db: Session, email: str):
    user = db.query(Usuario).filter(Usuario.email == email).first()

    # Por segurança, não informamos ao cliente se o e-mail foi encontrado ou não.
    # A mensagem de retorno é a mesma em ambos os casos.
    if user:
        # Gerar e salvar a nova senha
        nova_senha = gerar_senha(8)
        user.senha_hash = hash_senha(nova_senha)
        db.commit()

        # Preparar e enviar o e-mail
        subject = "Redefinição de Senha - Sistema TTG"
        body = f"""
        <html>
            <body>
                <p>Olá, {user.nome},</p>
                <p>Uma redefinição de senha foi solicitada para sua conta.</p>
                <p>Sua nova senha é: <strong>{nova_senha}</strong></p>
                <br>
                <p>Atenciosamente,</p>
                <p>Equipe TTG</p>
            </body>
        </html>
        """
        await send_email(recipient_email=user.email, subject=subject, body=body)

    return {"message": "Se existir uma conta com o e-mail informado, uma nova senha foi enviada."}

def get_user_role(db: Session, user_id: int) -> str:
    # 1) Verifica se é Orientador de Gestão de Projeto
    orientador = db.query(models.Orientador).filter(
        models.Orientador.id_usuario == user_id,
        models.Orientador.id_tipo_orientador == 2  # 2 = Gestão de Projeto
    ).first()
    if orientador:
        return "adm"

    # 2) Verifica se é Aluno
    aluno = db.query(models.Aluno).filter(
        models.Aluno.id_usuario == user_id
    ).first()
    if aluno:
        return "aluno"

    # 3) Se não cair em nenhum caso
    return "aluno"
