from sqlalchemy.orm import Session
import logging
from app.db.session import Base, engine
from app.models.user import User
from app.models.exchange import Exchange
from app.models.strategy import Strategy
from app.core.security import get_password_hash
from app.config import settings

logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    """Inicializa la base de datos con las tablas y datos iniciales"""
    try:
        # Crear tablas
        Base.metadata.create_all(bind=engine)
        logger.info("Base de datos inicializada correctamente")
        
        # Verificar si ya existe un usuario administrador
        user = db.query(User).filter(User.email == "admin@tradingroad.com").first()
        if not user:
            # Crear usuario administrador por defecto
            admin_user = User(
                email="admin@tradingroad.com",
                hashed_password=get_password_hash("admin"),  # Cambiar en producción
                full_name="Administrador",
                is_active=True,
                is_superuser=True,
                user_level="admin"
            )
            db.add(admin_user)
            db.commit()
            logger.info("Usuario administrador creado correctamente")
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {e}")
        raise
