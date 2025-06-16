from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import engine, SessionLocal
from app.db.init_db import init_db
from app.routes.api import api_router
from app.dashboard import create_dash_app
# Usaremos configuración directa de templates en lugar de importar

# Inicializar FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# import para logging y middleware de sesiones
import logging
logger_main = logging.getLogger(__name__)
from starlette.middleware.sessions import SessionMiddleware

# Configuración inicial de middlewares en la aplicación FastAPI original
logger_main.warning(f"MAIN.PY: Preparando para configurar middlewares. SECRET_KEY: '{settings.SECRET_KEY}' (Tipo: {type(settings.SECRET_KEY)})")

# Configurar middleware de seguridad en producción
if settings.ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# Middleware para compresión (TEMPORALMENTE COMENTADO PARA DEBUG)
# app.add_middleware(GZipMiddleware, minimum_size=1000)

# Middleware para CORS (TEMPORALMENTE COMENTADO PARA DEBUG)
# origins = settings.CORS_ORIGINS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
#     expose_headers=["Content-Type", "Authorization"],
#     max_age=600,  # Tiempo de caché para preflight (10 minutos)
# )

# Configuración de rutas para archivos estáticos y plantillas
import os

# Prueba con diferentes rutas posibles para el entorno de Render y desarrollo local
potential_base_dirs = [
    # Ruta estándar: subir un nivel desde el directorio actual
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    # Ruta alternativa: el directorio raiz del proyecto en Render
    "/opt/render/project/src",
    # Ruta alternativa: el directorio actual (por si acaso)
    os.path.dirname(os.path.abspath(__file__))
]

# Buscar las carpetas templates y static en las posibles ubicaciones
templates_dir = None
static_dir = None

for base in potential_base_dirs:
    # Comprobar si existe el directorio de templates
    test_templates = os.path.join(base, "templates")
    if os.path.isdir(test_templates):
        templates_dir = test_templates
        # Si encontramos templates, ver si static está en el mismo nivel
        test_static = os.path.join(base, "static")
        if os.path.isdir(test_static):
            static_dir = test_static
        break

# Si aún no hemos encontrado static, buscarlo de nuevo
if static_dir is None:
    for base in potential_base_dirs:
        test_static = os.path.join(base, "static")
        if os.path.isdir(test_static):
            static_dir = test_static
            break

# Si no se encuentran las carpetas, usar las rutas por defecto
if templates_dir is None:
    templates_dir = os.path.join(potential_base_dirs[0], "templates")
    logger_main.error(f"MAIN.PY: No se encontró el directorio de templates, usando ruta por defecto: {templates_dir}")

if static_dir is None:
    static_dir = os.path.join(potential_base_dirs[0], "static")
    logger_main.error(f"MAIN.PY: No se encontró el directorio de archivos estáticos, usando ruta por defecto: {static_dir}")

# Registrar las rutas encontradas
logger_main.warning(f"MAIN.PY: Montando archivos estáticos desde: {static_dir}")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

logger_main.warning(f"MAIN.PY: Directorio de templates configurado en: {templates_dir}")
templates = Jinja2Templates(directory=templates_dir)

# OAuth2 configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login")

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Incluir router centralizado de API
app.include_router(api_router, prefix=settings.API_V1_STR)

# Ruta principal de FastAPI que renderiza la plantilla base
@app.get("/", tags=["root"])
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": settings.PROJECT_NAME})

# Middleware para proteger rutas del dashboard
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Intentar acceder a la sesión para CUALQUIER ruta para diagnóstico
    try:
        # La simple presencia de request.session ya haría el assert si falla
        _ = request.session 
    except AssertionError as e:
        # Este log es útil para saber si la sesión está disponible en general para este middleware
        logger_main.error(f"AUTH_MIDDLEWARE: General AssertionError accessing request.session: {e} (Ruta: {request.url.path})")
        # No detenemos la solicitud aquí todavía, para que el endpoint pueda intentarlo también,
        # o para que la lógica de /dashboard/ pueda decidir una redirección.

    if request.url.path.startswith("/dashboard/"): # Asegurar la barra al final
        access_token = None
        try:
            # Intentar obtener el token de la sesión
            access_token = request.session.get("access_token")
        except AssertionError as e:
            # Si request.session falla aquí, es el mismo problema que el log anterior.
            # Para /dashboard/, la falta de sesión (por cualquier motivo) debe redirigir.
            logger_main.warning(f"AUTH_MIDDLEWARE: AssertionError for /dashboard/ session access: {e}. Redirecting to login.")
            # URL hardcoded para evitar lookup de nombre de ruta
            return RedirectResponse(url="/api/v1/auth/login_form", status_code=303)

        if not access_token:
            # Si no hay token de acceso en la sesión (aunque la sesión exista)
            logger_main.info(f"AUTH_MIDDLEWARE: No access_token in session for {request.url.path}. Redirecting to login.")
            return RedirectResponse(url="/api/v1/auth/login_form", status_code=303)
    
    # Continuar con la solicitud y obtener la respuesta del siguiente manejador
    response = await call_next(request)
    return response

# Crear e integrar la aplicación Dash con ruta consistente
dash_app = create_dash_app("/dashboard/")  # Con slash final
# Montar la aplicación Dash en FastAPI
app.mount("/dashboard", dash_app.server)  # Sin slash final

@app.on_event("startup")
async def startup_event():
    # Inicializar la base de datos
    db = next(get_db())
    init_db(db)

# IMPORTANTE: Este es el último paso, después de configurar todo lo demás:
# Aplicar SessionMiddleware como capa externa final
logger_main.warning(f"MAIN.PY: Aplicando SessionMiddleware como capa externa final")
app = SessionMiddleware(app, secret_key=settings.SECRET_KEY)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
