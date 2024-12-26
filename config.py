import os
from dotenv import load_dotenv

load_dotenv(override=True) 

class Config:
    SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = float(os.getenv('JWT_ACCESS_TOKEN_EXPIRES')) 
    JWT_REFRESH_TOKEN_EXPIRES =float(os.getenv('JWT_REFRESH_TOKEN_EXPIRES')) 
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION')
    BUCKET_NAME = os.getenv('BUCKET_NAME')
    SECRET_KEY_GEMINI= os.getenv('SECRET_KEY_GEMINI')
