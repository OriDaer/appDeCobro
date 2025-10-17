import os
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "clave_por_defecto"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "mysql+pymysql://root:root@localhost/app_cobro"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MERCADOPAGO_ACCESS_TOKEN = os.environ.get("MERCADOPAGO_ACCESS_TOKEN")
    MERCADOPAGO_PUBLIC_KEY = os.environ.get("MERCADOPAGO_PUBLIC_KEY")
