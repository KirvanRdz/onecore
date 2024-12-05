import io
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt, get_jwt_identity
from datetime import timedelta
import boto3
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Crear la app
app = Flask(__name__)

# Configurar clave secreta para JWT
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)


# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.getenv('SQLALCHEMY_DATABASE_URI')
)

# Inicializar JWT y SQLAlchemy
jwt = JWTManager(app)
db = SQLAlchemy(app)

# Inicializar Flask-Migrate
migrate = Migrate(app, db)

# Modelo para almacenar los datos procesados
class Data(db.Model):
    __tablename__ = 'data'
    id = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(255), nullable=False)  
    Edad = db.Column(db.Integer, nullable=False)  
    Fecha_nacimiento = db.Column(db.Date, nullable=False)

# Datos ficticios de usuario
USERS = {
    "test": {
        "password": "test",
        "id_usuario": 1,
        "rol": "admin"
    }
}

# Endpoint de inicio de sesión
@app.route('/login', methods=['POST'])
def login():
    data = request.json

    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    username = data['username']
    password = data['password']

    user = USERS.get(username)
    if not user or user['password'] != password:
        return jsonify({"error": "Credenciales inválidas"}), 401

    additional_claims={"rol": user['rol']}
    access_token = create_access_token(username, additional_claims=additional_claims)
    

    return jsonify(access_token=access_token)

# Configuración de AWS S3
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

BUCKET_NAME = os.getenv('BUCKET_NAME')

# Endpoint para subir archivo
@app.route('/upload', methods=['POST'])
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
    validation_errors = []
    required_columns = ['Nombre', 'Edad', 'Fecha_nacimiento']

    # Validar columnas requeridas
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        validation_errors.append(f"Faltan columnas obligatorias: {', '.join(missing_columns)}")
    
    # Validar si el archivo está vacío
    if df.empty:
        validation_errors.append("El archivo CSV está vacío")

    # Validar valores vacíos
    if df.isnull().values.any():
        validation_errors.append("El archivo contiene valores vacíos")

    # Validar duplicados
    if df.duplicated().any():
        validation_errors.append("El archivo contiene filas duplicadas")

    # Validar tipos de datos
    try:
        df['Nombre'] = df['Nombre'].astype(str)
        df['Edad'] = df['Edad'].astype(int)
        df['Fecha_nacimiento'] = pd.to_datetime(df['Fecha_nacimiento'])
    except Exception as e:
        validation_errors.append(f"Error en tipos de datos: {str(e)}")

    # Si hay errores de validación, devolverlos
    if validation_errors:
        return jsonify({
            "message": "El archivo no cumple con las validaciones requeridas",
            "validations": validation_errors
        }), 400

    # Subir archivo a AWS S3
    try:
        file.seek(0)
        s3_client.upload_fileobj(file, BUCKET_NAME, file.filename)
    except Exception as e:
        return jsonify({"error": f"Error al subir a S3: {str(e)}"}), 500

    # Guardar contenido en la base de datos
    try:
        for _, row in df.iterrows():
            data_entry = Data(
                Nombre=row['Nombre'], 
                Edad=row['Edad'], 
                Fecha_nacimiento=row['Fecha_nacimiento']
            )
            db.session.add(data_entry)
        db.session.commit()
    except Exception as e:
        return jsonify({"error": f"Error al guardar en la base de datos: {str(e)}"}), 500

    # Si todo se procesó correctamente
    return jsonify({
        "message": "Archivo procesado y almacenado correctamente",
        "validations": ["El archivo pasó todas las validaciones"]
    }), 200


# Endpoint para la renovación del JWT
@app.route('/refresh_token', methods=['POST'])
@jwt_required()  # Verifica automáticamente que el token no esté expirado
def refresh_token():
    # Extraer información del token actual
    claims = get_jwt()
    additional_claims={"rol": claims['rol']}
    # Generar un nuevo token con tiempo adicional
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user, additional_claims=additional_claims, expires_delta=timedelta(minutes=15))

    return jsonify(access_token=new_token), 200


if __name__ == '__main__':
    app.run(debug=True)
