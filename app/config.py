import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Tuple, Dict, Any, ClassVar

# Cargar variables de entorno desde .env
load_dotenv()

class Settings(BaseSettings):
    # Configuración general
    PROJECT_NAME: str = "TradingRoad"
    PROJECT_DESCRIPTION: str = "Plataforma de trading con análisis en tiempo real"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "clave_secreta_por_defecto_cambiarme")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 días
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")  # development, testing, production
    
    # Configuración CORS
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:8000")
    CORS_ORIGINS: Tuple[str, ...] = (
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://tradingroad.onrender.com",
    )
    
    # Configuración de base de datos
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./tradingroad.db"
    )
    
    # Configuración de email
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAILS_FROM_EMAIL: str = os.getenv("EMAILS_FROM_EMAIL", "info@tradingroad.com")
    EMAILS_FROM_NAME: str = os.getenv("EMAILS_FROM_NAME", "TradingRoad")
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "AIzaSyCaijxBkHVI05Y2uYz6iU5tgxxz8oUlUok")
    
    # Niveles de usuario
    USER_LEVELS: ClassVar[Dict[str, Dict[str, Any]]] = {
        "basic": {
            "name": "Básico",
            "max_exchanges": 1,
            "max_strategies": 2,
            "allow_backtesting": False,
            "allow_live_trading": False
        },
        "standard": {
            "name": "Estándar",
            "max_exchanges": 2,
            "max_strategies": 5,
            "allow_backtesting": True,
            "allow_live_trading": False
        },
        "premium": {
            "name": "Premium",
            "max_exchanges": 5,
            "max_strategies": 10,
            "allow_backtesting": True,
            "allow_live_trading": True
        },
        "admin": {
            "name": "Administrador",
            "max_exchanges": 999,
            "max_strategies": 999,
            "allow_backtesting": True,
            "allow_live_trading": True
        }
    }

# Instancia de configuración para usar en la aplicación
settings = Settings()
