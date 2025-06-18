"""
TradingRoad - Aplicación principal
Integra FastAPI con plantillas Jinja2 para servir tanto la API como el frontend
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
import uvicorn
import os

# Importar la API existente
# Importar API
import sys
# Añadir la ruta del proyecto al path para poder importar correctamente
sys.path.insert(0, '/Users/jparedes/AppTrading/TradingRoad_Python')

# Crear una API independiente para las rutas de API
from fastapi import FastAPI

api_app = FastAPI(
    title="TradingRoad API",
    description="API para datos de trading y análisis técnico en tiempo real",
    version="1.0.0"
)

# Importamos directamente los routers
from api.app.routers import klines, indicators, exchanges, news

# Incluir los routers en la API
api_app.include_router(klines.router, prefix="/v1", tags=["klines"])
api_app.include_router(indicators.router, prefix="/v1", tags=["indicators"])
api_app.include_router(exchanges.router, prefix="/v1", tags=["exchanges"])
api_app.include_router(news.router, prefix="/v1", tags=["news"])

# Configurar la aplicación principal
app = FastAPI(
    title="TradingRoad",
    description="Plataforma avanzada de trading con análisis en tiempo real",
    version="1.0.0"
)

# Configurar CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar la API como subapp
app.mount("/api", api_app)

# Configurar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar plantillas
templates = Jinja2Templates(directory="templates")

# Simulación básica de autenticación (en producción usar sistema real)
def get_current_user(request: Request):
    # En producción usar sistema de autenticación real como JWT o OAuth
    # Por ahora simular usuario loggeado
    return {"username": "usuario_demo", "email": "demo@tradingroad.com"}

# Ruta raíz - página principal
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Rutas para autenticación (básicas para la demostración)
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/logout")
async def logout():
    # En producción, invalidar sesión/token
    return RedirectResponse(url="/")

# Rutas del dashboard (requieren autenticación simulada)
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_home(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("dashboard/home.html", {
        "request": request,
        "user": user,
        "active_page": "dashboard"
    })

@app.get("/dashboard/trading", response_class=HTMLResponse)
async def dashboard_trading(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("dashboard/trading.html", {
        "request": request,
        "user": user,
        "active_page": "trading"
    })

@app.get("/dashboard/analysis", response_class=HTMLResponse)
async def dashboard_analysis(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("dashboard/analysis.html", {
        "request": request,
        "user": user,
        "active_page": "analysis"
    })

@app.get("/dashboard/volatility", response_class=HTMLResponse)
async def dashboard_volatility(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("dashboard/volatility.html", {
        "request": request,
        "user": user,
        "active_page": "volatility"
    })

@app.get("/dashboard/news", response_class=HTMLResponse)
async def dashboard_news(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("dashboard/news.html", {
        "request": request,
        "user": user,
        "active_page": "news"
    })

# Manejo de página no encontrada
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("404.html", {
        "request": request
    }, status_code=404)

if __name__ == "__main__":
    # Ejecutar con: python main.py
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
