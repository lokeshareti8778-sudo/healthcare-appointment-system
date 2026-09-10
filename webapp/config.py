import os
from datetime import timedelta
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()


def database_uri() -> str:
    configured = os.getenv("DATABASE_URL")
    if configured:
        return configured.replace("postgres://", "postgresql+psycopg://", 1)

    password = quote_plus(os.getenv("POSTGRES_PASSWORD", ""))
    return (
        "postgresql+psycopg://"
        f"{os.getenv('POSTGRES_USER', 'postgres')}:{password}@"
        f"{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_DB', 'healthcare')}"
    )


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")
    SQLALCHEMY_DATABASE_URI = database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 300}
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    AZURE_FUNCTION_URL = os.getenv("AZURE_FUNCTION_URL", "")
    AZURE_FUNCTION_KEY = os.getenv("AZURE_FUNCTION_KEY", "")
    APPOINTMENT_FEE = int(os.getenv("APPOINTMENT_FEE", "800"))
