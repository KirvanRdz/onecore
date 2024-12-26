from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required
)
from datetime import timedelta
from config import Config

auth_bp = Blueprint('auth', __name__)

# Base de datos de usuarios simulada
USERS = {
    "admin": {
        "password": "test",
        "id_usuario": 1,
        "rol": "admin"
    }
}

# Configuración de tiempos de expiración
ACCESS_TOKEN_EXPIRES = timedelta(minutes=Config.JWT_ACCESS_TOKEN_EXPIRES)
REFRESH_TOKEN_EXPIRES = timedelta(days=Config.JWT_REFRESH_TOKEN_EXPIRES)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    username = data['username']
    password = data['password']
    user = USERS.get(username)
    if not user or user['password'] != password:
        return jsonify({"error": "Credenciales inválidas"}), 401

    # Crear tokens
    additional_claims = {"id_usuario": user['id_usuario'], "rol": user['rol']}
    access_token = create_access_token(identity=username, additional_claims=additional_claims, expires_delta=ACCESS_TOKEN_EXPIRES)
    refresh_token = create_refresh_token(identity=username, expires_delta=REFRESH_TOKEN_EXPIRES)

    return jsonify(access_token=access_token, refresh_token=refresh_token), 200

# Endpoint para la renovación del JWT
@auth_bp.route('/refresh_token', methods=['POST'])
@jwt_required(refresh=True)  # Asegura que se use un refresh_token válido
def refresh_token():
    current_user = get_jwt_identity()
    # Extraer el rol del usuario desde la base de datos o un almacenamiento confiable
    user = USERS.get(current_user)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Crear un nuevo access_token con las claims necesarias
    claims = {"rol": user["rol"]}
    new_access_token = create_access_token(identity=current_user, additional_claims=claims, expires_delta=ACCESS_TOKEN_EXPIRES)
    return jsonify(access_token=new_access_token), 200
