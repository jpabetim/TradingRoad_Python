# Guía de Inicio - TradingRoad Python

Esta guía te ayudará a poner en marcha el proyecto TradingRoad Python en tu entorno local.

## 1. Requisitos Previos

- Python 3.9 o superior
- pip (gestor de paquetes de Python)
- virtualenv (opcional pero recomendado)

## 2. Configuración del Entorno

### Crear y activar entorno virtual

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
# En macOS/Linux:
source venv/bin/activate
# En Windows:
# venv\Scripts\activate
```

### Instalar Dependencias

```bash
pip install -r requirements.txt
```

## 3. Configuración de Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto basado en `.env.example`:

```bash
cp .env.example .env
```

Edita el archivo `.env` según tu configuración local. Para desarrollo puedes usar SQLite:

```
DATABASE_URL=sqlite:///./app.db
```

## 4. Iniciar la Aplicación

### Método 1: Usando run.py

```bash
python run.py
```

### Método 2: Usando Uvicorn directamente

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 5. Acceso a la Aplicación

Una vez que la aplicación está en ejecución, puedes acceder a:

- **Frontend**: http://localhost:8000/
- **Dashboard**: http://localhost:8000/dashboard/
- **Documentación API**: http://localhost:8000/api/docs

## 6. Ejecutar Pruebas

Para ejecutar las pruebas automáticas:

```bash
pytest
```

Para ejecutar pruebas específicas:

```bash
pytest tests/test_auth.py -v
```

## 7. Estructura de Directorios

La aplicación sigue esta estructura:

```
TradingRoad_Python/
├── app/                        # Código principal
│   ├── dashboard/              # Interfaz Dash
│   ├── db/                     # Configuración de BD
│   ├── models/                 # Modelos SQLAlchemy
│   ├── routes/                 # Rutas API
│   ├── schemas/                # Esquemas Pydantic
│   └── core/                   # Funcionalidades centrales
├── static/                     # Archivos estáticos
├── templates/                  # Plantillas HTML
└── tests/                      # Pruebas
```

## 8. Usuario Administrador por Defecto

La aplicación crea automáticamente un usuario administrador:

- **Email**: admin@tradingroad.com
- **Contraseña**: admin

**¡IMPORTANTE!**: Cambia estas credenciales en un entorno de producción.

## 9. Despliegue en Render.com

El archivo `render.yaml` está configurado para desplegar la aplicación en Render.com:

1. Crea una cuenta en Render.com
2. Conecta tu repositorio de GitHub
3. Configura un nuevo servicio web usando la opción "Blueprint"
4. Configura las variables de entorno necesarias

## 10. Solución de Problemas

### Base de datos

Si encuentras errores relacionados con la base de datos, puedes resetearla:

```bash
rm app.db
python -c "from app.db.init_db import init_db; from app.db.session import SessionLocal; init_db(SessionLocal())"
```

### Dependencias

Si hay problemas con las dependencias:

```bash
pip install --upgrade -r requirements.txt
```
