from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.utils.aws import upload_to_s3
from app.utils.validation import validate_csv
from app.services.dataServices import save_data
import pandas as pd
import io

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/', methods=['POST'])
@jwt_required()
def upload_file():
    claims = get_jwt()
    
    # Restringir acceso según rol
    if claims['rol'] != 'admin':
        return jsonify({"error": "No tienes permiso para realizar esta acción"}), 403

    # Verificar que se haya enviado un archivo
    if 'file' not in request.files:
        return jsonify({"error": "No se envió un archivo"}), 400
    
    # Verificar que se hayan enviado parámetros adicionales
    param1 = request.form.get('param1')
    param2 = request.form.get('param2')
    if not param1 or not param2:
        return jsonify({"error": "Faltan parámetros adicionales: param1 y param2 son requeridos"}), 400
    

    file = request.files['file']
    if not file.filename.endswith('.csv'):
        return jsonify({"error": "El archivo debe ser un CSV"}), 400

    try:
        # Leer archivo CSV
        file_content = file.read()
        file_stream = io.BytesIO(file_content)
        df = pd.read_csv(file_stream)
    except Exception as e:
        return jsonify({"error": f"Error al leer el archivo: {str(e)}"}), 400
    
    # Validaciones del archivo
    validation_errors = validate_csv(df)
    if validation_errors:
        return jsonify({"message": "El archivo no cumple con las validaciones requeridas", "validations": validation_errors}), 400

    # Subir archivo a AWS S3
    try:
        file.seek(0) # Asegura que el puntero esté al inicio del archivo
        upload_to_s3(file, file.filename)
    except Exception as e:
        return jsonify({"error": f"Error al subir a S3: {str(e)}"}), 500

    # Guardar contenido en la base de datos
    try:
        save_data(df)
    except Exception as e:
        return jsonify({"error": f"Error al guardar en la base de datos: {str(e)}"}), 500

    return jsonify({"message": "Archivo procesado y almacenado correctamente", "validations": ["El archivo pasó todas las validaciones"]}), 200
