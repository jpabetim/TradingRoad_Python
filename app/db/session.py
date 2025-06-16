from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import sys
import logging
import re

from app.config import settings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Verificar y corregir formato de URL para compatibilidad con Render
try:
    database_url = settings.DATABASE_URL
    
    # Imprimir información de diagnóstico (se mostrará en los logs de Render)
    logger.info(f"DATABASE_URL tipo: {type(database_url)}")
    if database_url:
        # No mostrar la URL completa por seguridad, solo el inicio
        safe_url = database_url[:15] + "..." if len(database_url) > 15 else database_url
        logger.info(f"DATABASE_URL comienza con: {safe_url}")
    else:
        logger.error("DATABASE_URL está vacía")
    
    # Solucionar problemas comunes con URLs
    if database_url is None or database_url == "":
        logger.warning("DATABASE_URL no está configurada, usando SQLite predeterminado")
        database_url = "sqlite:///./tradingroad.db"
    elif database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
        logger.info("Se corrigió formato postgres:// a postgresql://")
    
    # Validar que la URL de PostgreSQL tenga formato correcto
    if database_url.startswith("postgresql://"):
        # Verificar si la URL tiene el patrón correcto
        if not re.match(r'postgresql://[^:]+:[^@]+@[^/:]+(?::\d+)?/[^/]+', database_url):
            logger.error(f"La URL de PostgreSQL parece estar mal formada. Usando SQLite como fallback.")
            database_url = "sqlite:///./tradingroad.db"

    # Crear motor de base de datos
    engine = create_engine(
        database_url, 
        pool_pre_ping=True,
        connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {}
    )
    logger.info("Motor de base de datos creado exitosamente")
    
except Exception as e:
    logger.error(f"Error al configurar la base de datos: {str(e)}")
    logger.error(f"Variables de entorno disponibles: {list(os.environ.keys())}")
    # Usar SQLite como fallback
    logger.warning("Usando SQLite como base de datos de respaldo")
    database_url = "sqlite:///./tradingroad_fallback.db"
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False}
    )

# Crear sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear base para modelos ORM
Base = declarative_base()
