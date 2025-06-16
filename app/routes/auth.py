from fastapi import APIRouter, Depends, HTTPException, status, Body, Security, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any, List

from app import models, schemas
from app.core import security, deps
from app.core.templates import templates
from app.config import settings
from datetime import timedelta

router = APIRouter()

# Ruta para servir la página de login
@router.get("/login_form", response_class=HTMLResponse)
async def login_form_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "title": "Iniciar Sesión"})

# Ruta para servir la página de registro
@router.get("/register", response_class=HTMLResponse)
async def register_form_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "title": "Registro"})

@router.post("/login")
async def login_access_token(
    request: Request,
    db: Session = Depends(deps.get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Login con usuario y contraseña
    """
    # Buscar usuario por email
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    # Verificar que el usuario existe y la contraseña es correcta
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "title": "Iniciar Sesión", "error": "Correo o contraseña incorrectos"}
        )
    
    # Verificar que el usuario está activo
    if not user.is_active:
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "title": "Iniciar Sesión", "error": "Usuario inactivo"}
        )
    
    # Determinar los scopes según el nivel de usuario
    scopes = ["user"]
    if user.is_superuser:
        scopes.append("admin")
    
    # Crear token de acceso
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Incluir scopes en el token
    token_data = {"sub": user.email, "scopes": scopes}
    
    # Generar el token JWT
    access_token = security.create_access_token(
        token_data, expires_delta=access_token_expires
    )
    
    # Guardar el token en la sesión
    request.session["access_token"] = access_token
    request.session["token_type"] = "bearer"
    request.session["user_email"] = user.email
    
    # Redireccionar a la página principal
    response = RedirectResponse(url="/", status_code=303)
    return response

@router.post("/register", response_model=schemas.User)
async def register_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
) -> Any:
    """
    Registrar un nuevo usuario
    """
    # Verificar si ya existe un usuario con este email
    user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con este correo electrónico",
        )
    
    # Crear usuario
    user = models.User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name,
        user_level=user_in.user_level,
        is_active=user_in.is_active,
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@router.get("/me", response_model=schemas.User)
async def get_me(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Obtener información del usuario actual
    """
    return current_user

@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    current_password: str = Body(...),
    new_password: str = Body(...),
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Cambiar la contraseña del usuario
    """
    # Verificar contraseña actual
    if not security.verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta",
        )
    
    # Actualizar contraseña
    current_user.hashed_password = security.get_password_hash(new_password)
    db.add(current_user)
    db.commit()
    
    return {"message": "Contraseña actualizada correctamente"}
