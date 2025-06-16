from fastapi.templating import Jinja2Templates
import os
import pathlib

# Obtener ruta absoluta al directorio base del proyecto
BASE_DIR = pathlib.Path(__file__).parent.parent.parent

# Configurar Jinja2Templates con ruta absoluta
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
