from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session
from typing import Generator, Optional, List

from app import models, schemas
from app.config import settings
from app.db.session import SessionLocal
from app.core.security import verify_password
from datetime import datetime

# Configurar OAuth2
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    scopes={
        "user": "Usuario normal",
        "admin": "Acceso de administrador"
    }
)

def get_db() -> Generator:
    """
    Dependencia para obtener una sesión de base de datos
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    security_scopes: SecurityScopes,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> models.User:
    """
    Dependencia para obtener el usuario actual a partir del token JWT
    """
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    try:
        # Decodificar token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        # Validar token_data
        token_data = schemas.TokenData(
            username=username,
            scopes=payload.get("scopes", [])
        )
    except (JWTError, ValidationError):
        raise credentials_exception
    
    # Buscar usuario en la base de datos
    user = db.query(models.User).filter(models.User.email == token_data.username).first()
    if user is None:
        raise credentials_exception
    
    # Verificar que el usuario esté activo
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    
    # Verificar scopes
    if security_scopes.scopes and not any(
        scope in token_data.scopes for scope in security_scopes.scopes
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes suficientes permisos para esta acción",
            headers={"WWW-Authenticate": authenticate_value},
        )
    
    return user

def get_current_active_user(
    current_user: models.User = Security(get_current_user, scopes=["user"])
) -> models.User:
    """
    Dependencia para obtener el usuario actual activo
    """
    return current_user

def get_current_admin_user(
    current_user: models.User = Security(get_current_user, scopes=["admin"])
) -> models.User:
    """
    Dependencia para obtener el usuario administrador actual
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes suficientes privilegios"
        )
    return current_user
