#!/usr/bin/env python3
"""
Script para probar el arranque de la aplicación con Uvicorn
"""
import os
import sys
import logging
import subprocess
import time
import requests
import signal
import random

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_startup")

def test_uvicorn_startup():
    """Prueba el arranque de la aplicación con Uvicorn"""
    try:
        # Seleccionar un puerto aleatorio entre 9000 y 9999 para evitar conflictos
        port = random.randint(9000, 9999)
        logger.info(f"Iniciando la aplicación con Uvicorn en puerto {port}...")
        cmd = ["python3", "run.py", "--port", str(port)]
        
        # Usar Popen para no bloquear este script
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        # Esperar a que la aplicación se inicie (máximo 10 segundos)
        logger.info("Esperando a que la aplicación se inicie...")
        max_attempts = 10
        for i in range(max_attempts):
            try:
                time.sleep(1)  # Esperar 1 segundo entre intentos
                # Probar acceso a la raíz
                response = requests.get(f"http://localhost:{port}/")
                if response.status_code == 200:
                    logger.info(f"La aplicación se inició correctamente. Código de respuesta: {response.status_code}")
                    break
                else:
                    logger.warning(f"La aplicación respondió con código: {response.status_code}")
            except requests.exceptions.RequestException:
                if i == max_attempts - 1:
                    logger.error("No se pudo conectar a la aplicación después de múltiples intentos")
                else:
                    logger.info(f"Intento {i+1}/{max_attempts}: La aplicación aún no está lista...")
        
        # Probar algunas rutas clave para verificar redirecciones y endpoints
        try:
            # Probar redirección de /v1/auth/login_form a /api/v1/auth/login_form
            logger.info("Probando redirección de rutas /v1/auth/...")
            response = requests.get(f"http://localhost:{port}/v1/auth/login_form", allow_redirects=False)
            if response.status_code == 301:
                redirect_url = response.headers.get('Location', '')
                logger.info(f"Redirección correcta a: {redirect_url}")
            else:
                logger.warning(f"Redirección no funcionó como se esperaba. Código: {response.status_code}")
            
            # Probar acceso a la API
            logger.info("Probando acceso a API...")
            response = requests.get(f"http://localhost:{port}/api/v1/")
            logger.info(f"Respuesta de API: {response.status_code}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al probar rutas: {e}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error al iniciar Uvicorn: {e}")
        return False
    finally:
        # Asegurar que el proceso se termine correctamente
        if 'process' in locals():
            logger.info("Deteniendo la aplicación...")
            process.send_signal(signal.SIGINT)  # Enviar Ctrl+C
            process.wait(timeout=5)  # Esperar a que termine

if __name__ == "__main__":
    success = test_uvicorn_startup()
    if success:
        logger.info("Prueba de arranque completada.")
        sys.exit(0)
    else:
        logger.error("Prueba de arranque falló.")
        sys.exit(1)
