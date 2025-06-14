"""
Script para ejecutar TradingRoad en modo desarrollo.

Uso:
    python run.py
"""
import uvicorn
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", "8000")), 
        reload=True,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
