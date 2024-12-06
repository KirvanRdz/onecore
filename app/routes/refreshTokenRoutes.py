from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity, create_access_token
from datetime import timedelta

refresh_bp = Blueprint('refresh', __name__)

# Endpoint para la renovación del JWT
@refresh_bp.route('/token', methods=['POST'])
@jwt_required() # Verifica automáticamente que el token no esté expirado
def refresh_token():
    current_user = get_jwt_identity()
    claims = {"rol": get_jwt()["rol"]}
    new_token = create_access_token(identity=current_user, additional_claims=claims,expires_delta=timedelta(minutes=15))
    return jsonify(access_token=new_token), 200
