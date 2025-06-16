from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import engine, SessionLocal
from app.db.init_db import init_db
from app.routes.api import api_router
from app.dashboard import create_dash_app
from app.core.templates import templates

# Inicializar FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configurar middleware de seguridad en producción
if settings.ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# Middleware para compresión
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Middleware para CORS
origins = settings.CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "Authorization"],
    max_age=600,  # Tiempo de caché para preflight (10 minutos)
)

# Middleware para sesiones
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

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
    if request.url.path.startswith("/dashboard"):
        # Verificar si hay una sesión
        session = request.cookies.get("session")
        if not session:
            # Redirigir al login si no hay sesión
            return RedirectResponse(url="/api/v1/auth/login_form")
    
    # Continuar con la solicitud normalmente
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
