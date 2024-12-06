from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)

USERS = {
    "test": {
        "password": "test",
        "id_usuario": 1,
        "rol": "admin"
    }
}

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

    additional_claims = {"rol": user['rol']}
    access_token = create_access_token(username, additional_claims=additional_claims)
    return jsonify(access_token=access_token)
