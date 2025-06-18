"""
TradingRoad API - Aplicación principal
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# Importar routers
from app.routers import klines, indicators, exchanges, news, auth

app = FastAPI(
    title="TradingRoad API",
    description="API para datos de trading y análisis técnico en tiempo real",
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

# Incluir los routers
app.include_router(klines.router, prefix="/api/v1", tags=["klines"])
app.include_router(indicators.router, prefix="/api/v1", tags=["indicators"])
app.include_router(exchanges.router, prefix="/api/v1", tags=["exchanges"])
app.include_router(news.router, prefix="/api/v1", tags=["news"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

@app.get("/", tags=["root"])
async def root():
    """Endpoint raíz que muestra información básica de la API"""
    return {
        "name": "TradingRoad API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": [
            {"path": "/api/v1/klines", "description": "Datos OHLCV para gráficos de velas"},
            {"path": "/api/v1/indicators", "description": "Cálculo de indicadores técnicos"},
            {"path": "/api/v1/exchanges", "description": "Información sobre exchanges y pares disponibles"},
            {"path": "/api/v1/news", "description": "Noticias"},
            {"path": "/api/v1/auth", "description": "Autenticación de usuarios"}
        ]
    }

if __name__ == "__main__":
    # Ejecutar con: python -m app.main
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
