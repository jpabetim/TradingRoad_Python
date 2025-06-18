import uvicorn
import os
import sys

# Añadir directorio raíz al path para importaciones
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    # Ejecutar la API FastAPI
    uvicorn.run(
        "api.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-recarga en desarrollo
        workers=1
    )
