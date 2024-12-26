import boto3
from config import Config

def upload_to_s3(file, filename):
    """
    Sube un archivo a un bucket de AWS S3.

    Parámetros:
    - file (werkzeug.datastructures.FileStorage): Archivo que se desea subir al bucket.
    - filename (str): Nombre con el que se almacenará el archivo en el bucket de S3.

    Retorna:
    - None: No retorna ningún valor.
    """
    s3_client = boto3.client(
        's3',
        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
        region_name=Config.AWS_REGION
    )
    s3_client.upload_fileobj(file, Config.BUCKET_NAME, filename)

def textract_aws():
    """
    Inicializa y devuelve un cliente de AWS Textract.

    Parámetros:
    - No recibe parámetros.
    
    Retorna:
    - boto3.client: Un cliente de AWS Textract configurado con las credenciales y región especificadas en la configuración.
    """
    return boto3.client(
        'textract',
        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
        region_name=Config.AWS_REGION
    )
     

