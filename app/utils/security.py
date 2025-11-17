# app/utils/security.py

import random
import string
from passlib.hash import bcrypt

def gerar_senha(comprimento: int = 8) -> str:
    """
    Gera uma senha aleatória de 8 caracteres com exatamente 2 números
    e 6 letras maiúsculas, em posições aleatórias.
    """
    # Garante 2 caracteres numéricos
    numeros = ''.join(random.choice(string.digits) for _ in range(2))
    
    # Garante 6 caracteres de letras maiúsculas
    letras = ''.join(random.choice(string.ascii_uppercase) for _ in range(6))
    
    # Combina os caracteres e embaralha a lista
    senha_lista = list(numeros + letras)
    random.shuffle(senha_lista)
    
    # Retorna a senha como uma string
    return ''.join(senha_lista)

def hash_senha(senha: str) -> str:
    return bcrypt.hash(senha)

def verificar_senha(senha: str, senha_hash: str) -> bool:
    return bcrypt.verify(senha, senha_hash)
