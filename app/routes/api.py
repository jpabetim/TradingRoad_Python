from fastapi import APIRouter

from app.routes import auth, exchange, analysis, strategy

# Router principal de la API
api_router = APIRouter()

# Registrar todos los routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(exchange.router, prefix="/exchanges", tags=["exchanges"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(strategy.router, prefix="/strategies", tags=["strategies"])
