from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta
from config import Config

def create_tokens(username, user_data):
    """Genera JWT de acceso y refresh token para el usuario."""
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
