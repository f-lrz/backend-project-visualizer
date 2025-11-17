import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import BaseModel, EmailStr
from typing import List


class EmailSchema(BaseModel):
    email: List[EmailStr]


# Configuração carregada a partir das variáveis de ambiente
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=os.getenv("MAIL_STARTTLS", "True").lower() == "true",
    MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS", "False").lower() == "true",
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


async def send_email(recipient_email: str, subject: str, body: str):
    """
    Envia um e-mail para o destinatário especificado.
    """
    try:
        message = MessageSchema(
            subject=subject,
            recipients=[recipient_email],
            body=body,
            subtype="html"
        )

        fm = FastMail(conf)
        await fm.send_message(message)
        print(f"E-mail enviado para {recipient_email}")
    except Exception as e:
        print(f"Erro ao enviar e-mail para {recipient_email}: {e}")
