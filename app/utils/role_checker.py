from fastapi import Depends, HTTPException, status
from app.utils.jwt_bearer import get_current_user

def role_required(required_roles: list[str] | str):
    """
    Valida se o usuário logado possui a role necessária.
    Pode receber uma role única ("adm") ou lista de roles (["adm", "aluno"]).
    """
    if isinstance(required_roles, str):
        required_roles = [required_roles]

    def wrapper(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        if user_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Requer {required_roles}, mas você é '{user_role}'."
            )
        return current_user
    return wrapper
