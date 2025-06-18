from fastapi import APIRouter, Request, Form, Depends, Cookie, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import JSONResponse
from starlette.status import HTTP_303_SEE_OTHER
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
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    # Simulamos autenticación básica - en producción verificaríamos con la base de datos
    logger.info(f"Intento de login para usuario: {username}")
    
    # En producción tendríamos verificación real de password
    # Aquí simplemente simulamos un login exitoso
    
    # Creamos una sesión autenticada
    request.session["authenticated"] = True
    request.session["username"] = username
    
    # Guardar la sesión explícitamente
    logger.info(f"Creada sesión para usuario {username}")
    
    # En vez de usar RedirectResponse, construimos una respuesta manual
    response = RedirectResponse(url="/dashboard/", status_code=HTTP_303_SEE_OTHER)
    
    # Devolvemos la respuesta con la sesión ya establecida
    return response

@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    logger.info("Procesando solicitud de formulario de registro")
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register(request: Request, username: str = Form(...), password: str = Form(...)):
    # Aquí iría la lógica real de registro
    logger.info(f"Intento de registro para usuario: {username}")
    
    # Simular registro exitoso
    # En una aplicación real, guardaríamos en base de datos
    
    # Redirigir a login
    return RedirectResponse(url="/api/v1/auth/login_form", status_code=HTTP_303_SEE_OTHER)

@router.get("/logout")
async def logout(request: Request):
    # Eliminar datos de la sesión
    request.session.pop("authenticated", None)
    request.session.pop("username", None)
    logger.info("Usuario cerró sesión")
    
    # Redireccionar a la página principal
    return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)
