from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("auth_router")

# Crear el router con el prefijo correcto
router = APIRouter()

# Configurar templates
templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "templates")
templates = Jinja2Templates(directory=templates_dir)

# Rutas para formularios de autenticación
@router.get("/login_form", response_class=HTMLResponse)
async def login_form(request: Request):
    logger.info("Procesando solicitud de formulario de login")
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    # Aquí iría la lógica real de autenticación
    # Por ahora solo redirigimos al dashboard
    logger.info(f"Intento de login para usuario: {username}")
    return RedirectResponse(url="/dashboard/", status_code=303)

@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    logger.info("Procesando solicitud de formulario de registro")
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register(username: str = Form(...), password: str = Form(...)):
    # Aquí iría la lógica real de registro
    logger.info(f"Intento de registro para usuario: {username}")
    return RedirectResponse(url="/api/v1/auth/login_form", status_code=303)

@router.get("/logout")
async def logout():
    # Lógica de logout
    return RedirectResponse(url="/", status_code=303)
