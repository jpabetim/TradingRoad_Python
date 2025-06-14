from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Corregir formato de URL para compatibilidad con Render
database_url = settings.DATABASE_URL
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# Crear motor de base de datos
engine = create_engine(
    database_url, 
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {}
)

# Crear sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear base para modelos ORM
Base = declarative_base()
