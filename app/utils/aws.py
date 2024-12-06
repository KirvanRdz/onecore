import boto3
from config import Config

def upload_to_s3(file, filename):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
        region_name=Config.AWS_REGION
    )
    s3_client.upload_fileobj(file, Config.BUCKET_NAME, filename)
