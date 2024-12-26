from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.utils.aws import upload_to_s3
from app.utils.validation import validate_csv
from app.service.api.dataService import save_data
import pandas as pd
import io

upload_bp = Blueprint('data', __name__)

@upload_bp.route('/', methods=['POST'])
@jwt_required()
def upload_file():
    """
    Maneja la carga de archivos CSV, validando su contenido, subiéndolo a AWS S3 y almacenando los datos en la base de datos.

    Parámetros:
        - No requiere parámetros en el cuerpo de la solicitud. El archivo debe ser enviado como parte de un formulario con los campos 'file', 'param1' y 'param2'.
    
    Retorna:
        - Response: Un JSON con un mensaje de éxito si el archivo se procesa correctamente y pasa todas las validaciones.
        - Error: Si el archivo no cumple con las validaciones, si el usuario no tiene permisos, o si ocurre un error en cualquiera de los pasos (lectura del archivo, subida a S3 o almacenamiento en la base de datos).
    """

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
