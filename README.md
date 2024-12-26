# Desarrollo de Aplicación Web con Python y APIs

Este proyecto es una aplicación web desarrollada en Python utilizando Flask y herramientas de inteligencia artificial (IA) para la clasificación y extracción de datos de documentos cargados. La aplicación incluye integración con AWS Textract para la extracción de texto de documentos y Gemini de Google para la clasificación automática de los documentos.

## Tecnologías Utilizadas

* Python: Framework Flask para crear las APIs.
* AWS Textract: Para la extracción de texto de documentos.
* Gemini de Google: Para la clasificación automática de documentos.
* AWS S3: Para el almacenamiento de archivos cargados.
* SQL Server: Para almacenar los datos procesados de los archivos.
* JWT (JSON Web Token): Para autenticación y autorización de usuarios.
* GitHub: Control de versiones.
* Pytest: Para las pruebas unitarias.

## Funcionalidades
### APIs

1. Inicio de Sesión:

* Endpoint para que los usuarios anónimos inicien sesión y obtengan un JWT.

2. Carga y Validación de Archivos:

* Endpoint para subir un archivo CSV a AWS S3 y almacenar su contenido en SQL Server.
* Validación del archivo (valores vacíos, tipos incorrectos, duplicados).

3. Renovación de Token:

* Endpoint para renovar el JWT si el token original aún no ha expirado.

### Módulo de Análisis de Documentos

1. Clasificación Automática:

* Los documentos son clasificados automáticamente como Factura o Información usando Gemini de Google.

2. Extracción Automática de Datos:

* Facturas: Se extraen datos como cliente, proveedor, productos, número de factura, fecha y total.
* Información: Se extraen una descripción, resumen y análisis de sentimiento.

### Módulo Histórico

1. Registro de Eventos:

* Registra eventos como la carga de documentos, interacciones de IA, y acciones del usuario.
* Funcionalidades de filtrado y exportación de eventos a Excel.

## Instrucciones de Ejecución
### Requisitos
* Python 3.8+
* AWS Account con acceso a AWS S3 y AWS Textract.
* SQL Server o una base de datos compatible con SQLAlchemy.
* Una API KEY para Google Gemini

### Instalación
1. Clona el repositorio:
- `git clone https://github.com/KirvanRdz/onecore.git`
- `cd onecore`

2. Crea un entorno virtual y actívalo 
- `python -m venv venv`
- `env\Scripts\activate`

3. Instala las dependencias
- `pip install -r requirements.txt`

4. Configura las variables de entorno
- Crea un archivo .env en la raiz del pryecto, copia y pega el contendio de .example_env

### Ejecución de Migraciones
Este proyecto utiliza Flask-Migrate para manejar las migraciones de la base de datos. Para ejecutar las migraciones, sigue estos pasos:

1. Inicializa las migraciones:
- `flask db init`

2. Crea las migraciones para los modelos:
- `flask db migrate -m "Descripción de la migración"`

3. Aplica las migraciones a la base de datos:
- `flask db upgrade`

### Ejecución

1. Ejecuta la aplicación:
- `flask run`

Esto iniciará el servidor de desarrollo en http://127.0.0.1:5000

### Ejeuta Pruebas Unitarias
- `pytest`


## Endpoints para la API
- POST /api/auth/login: Inicia sesión para usuarios anónimos (requiere username y password).
- GET /api/auth/refresh_token: Renueva el ACCESS_TOKEN.
- POST /api/data: Carga un documento .csv, extrae los datos y los guarda en la base de datos.

## URLs para la Pantalla Web
http://127.0.0.1:5000/documents/: Pantalla para cargar documentos y realizar el análisis.

http://127.0.0.1:5000/logs/: Pantalla para visualizar el registro de eventos.

