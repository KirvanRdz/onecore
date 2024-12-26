from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta
from config import Config

def create_tokens(username, user_data):
    """
    Genera un token de acceso (JWT) y un token de refresco para el usuario.

    Parámetros:
    - username (str): Nombre de usuario o identidad del usuario para asociar con los tokens.
    - user_data (dict): Diccionario con información adicional (claims) que se incluirá en los tokens. 
      Ejemplo: {"id_usuario": int, "rol": str}.

    Retorna:
    - tuple: Una tupla con dos elementos:
        - access_token (str): Token de acceso firmado, válido por el tiempo configurado.
        - refresh_token (str): Token de refresco firmado, válido por el tiempo configurado.
    """
    access_token = create_access_token(
        identity=username,
        additional_claims=user_data,
        expires_delta=timedelta(minutes=Config.JWT_ACCESS_TOKEN_EXPIRES)
    )
    refresh_token = create_refresh_token(
        identity=username,
        additional_claims=user_data,
        expires_delta=timedelta(days=Config.JWT_REFRESH_TOKEN_EXPIRES)
    )
    return access_token, refresh_token
