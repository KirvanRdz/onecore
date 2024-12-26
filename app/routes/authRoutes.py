from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    get_jwt
)
from datetime import timedelta
from config import Config

auth_bp = Blueprint('auth', __name__)

# Configuración de tiempos de expiración
ACCESS_TOKEN_EXPIRES = timedelta(minutes=Config.JWT_ACCESS_TOKEN_EXPIRES)
REFRESH_TOKEN_EXPIRES = timedelta(days=Config.JWT_REFRESH_TOKEN_EXPIRES)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Faltan campos obligatorios: username y password son obligatorios"}), 400

    username = data['username']
    
    # Crear tokens
    additional_claims = {"id_usuario": 1, "rol": 'admin'}
    access_token = create_access_token(identity=username, additional_claims=additional_claims, expires_delta=ACCESS_TOKEN_EXPIRES)
    refresh_token = create_refresh_token(identity=username,additional_claims=additional_claims, expires_delta=REFRESH_TOKEN_EXPIRES)

    return jsonify(access_token=access_token, refresh_token=refresh_token), 200

# Endpoint para la renovación del JWT
@auth_bp.route('/refresh_token', methods=['POST'])
@jwt_required(refresh=True)  # valida refresh_token
def refresh_token():
    current_user = get_jwt_identity()  # Obtiene el nombre de usuario (identity) del JWT
    claims = get_jwt()  # Obtiene los claims adicionales (id_usuario, rol, etc.) del JWT

    # Acceder al rol directamente desde los claims
    rol = claims.get("rol")

    if not rol:
        return jsonify({"error": "Rol no encontrado en el token"}), 401

    # Crear un nuevo access_token con las claims necesarias
    new_access_token = create_access_token(identity=current_user, additional_claims=claims, expires_delta=ACCESS_TOKEN_EXPIRES)
    return jsonify(access_token=new_access_token), 200
