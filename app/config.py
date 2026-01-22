import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt_secret_key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:@localhost/secure_chat"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
