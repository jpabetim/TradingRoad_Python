# TradingRoad - Plataforma de Trading en Python

TradingRoad es una plataforma completa de trading desarrollada enteramente en Python que integra FastAPI como backend y Dash como frontend para proporcionar una experiencia de usuario fluida y potente tanto para análisis técnico como para trading en tiempo real.

## Características Principales

- **Arquitectura unificada en Python**: Backend y frontend integrados para un desarrollo más sencillo y eficiente
- **Análisis técnico avanzado**: Múltiples indicadores y herramientas de análisis de mercados financieros
- **Trading en tiempo real**: Conexión con múltiples exchanges (Binance, BingX, Bybit, etc.)
- **Análisis con IA**: Integración con Gemini AI para obtener insights avanzados sobre los mercados
- **Interfaz gráfica moderna**: Dashboards interactivos con Dash y Plotly
- **Seguridad**: Autenticación JWT, cifrado de credenciales y permisos por niveles de usuario

## Estructura del Proyecto

```
TradingRoad_Python/
│
├── app/                        # Código principal de la aplicación
│   ├── dashboard/              # Aplicación Dash integrada con FastAPI
│   │   ├── pages/              # Páginas del dashboard (home, trading, analysis, settings)
│   │   └── __init__.py         # Configuración de la app Dash
│   │
│   ├── db/                     # Configuración de base de datos
│   │   ├── session.py          # Sesión SQLAlchemy
│   │   └── init_db.py          # Inicialización de la BD
│   │
│   ├── models/                 # Modelos SQLAlchemy
│   │   ├── user.py             # Modelo de usuario
│   │   ├── exchange.py         # Modelo para conexiones de exchanges
│   │   └── strategy.py         # Modelo para estrategias de trading
│   │
│   ├── routes/                 # Rutas API REST
│   │   ├── auth.py             # Autenticación y usuarios
│   │   ├── exchange.py         # Gestión de exchanges
│   │   └── analysis.py         # Endpoints para análisis
│   │
│   ├── schemas/                # Esquemas Pydantic
│   │   ├── user.py             # Esquemas para usuarios
│   │   ├── exchange.py         # Esquemas para exchanges
│   │   └── strategy.py         # Esquemas para estrategias
│   │
│   ├── core/                   # Componentes centrales
│   │   ├── security.py         # Seguridad y autenticación
│   │   └── deps.py             # Dependencias para FastAPI
│   │
│   ├── config.py               # Configuración global
│   ├── main.py                 # Punto de entrada principal (FastAPI)
│   └── __init__.py             # Inicialización del paquete
│
├── static/                     # Archivos estáticos
│   ├── css/                    # Estilos CSS
│   ├── js/                     # JavaScript del cliente
│   └── img/                    # Imágenes
│
├── templates/                  # Plantillas HTML
│   └── index.html              # Página principal
│
├── tests/                      # Pruebas
│
├── .env                        # Variables de entorno (no incluido en git)
├── .env.example                # Ejemplo de variables de entorno
├── requirements.txt            # Dependencias del proyecto
└── README.md                   # Documentación del proyecto
```

## Instalación y Configuración

### Requisitos Previos

- Python 3.9+
- PostgreSQL (recomendado) o SQLite para desarrollo

### Pasos de Instalación

1. **Clonar el repositorio**

```bash
git clone https://github.com/tu-usuario/TradingRoad.git
cd TradingRoad_Python
```

2. **Crear y activar entorno virtual**

```bash
python -m venv venv
# En Windows
venv\Scripts\activate
# En macOS/Linux
source venv/bin/activate
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**

Copia `.env.example` a `.env` y configura las variables:

```bash
cp .env.example .env
# Edita el archivo .env con tus configuraciones
```

5. **Inicializar la base de datos**

```bash
python -m app.db.init_db
```

## Ejecución

Para iniciar la aplicación en modo desarrollo:

```bash
uvicorn app.main:app --reload
```

La aplicación estará disponible en:
- **API y Frontend**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/api/docs
- **Dashboard**: http://localhost:8000/dashboard/

## Autenticación y API

### Autenticación

La API utiliza autenticación JWT (JSON Web Tokens). Para obtener un token:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=tu-email@example.com" \
  -d "password=tu-contraseña"
```

### API Endpoints Principales

- **Autenticación**: `/api/v1/auth/login`, `/api/v1/auth/register`, `/api/v1/auth/me`
- **Exchanges**: `/api/v1/exchanges/`
- **Análisis**: `/api/v1/analysis/market-data/{symbol}`, `/api/v1/analysis/indicators/{symbol}`
- **IA**: `/api/v1/analysis/ai-analysis`

Consulta la documentación Swagger para más detalles: http://localhost:8000/api/docs

## Dashboard

El dashboard contiene varias páginas accesibles desde la interfaz principal:

- **Home**: Vista general del mercado y resumen de actividad
- **Trading**: Panel para trading en tiempo real
- **Analysis**: Herramientas de análisis técnico y con IA
- **Settings**: Configuración de usuario y conexiones

## Despliegue

Para despliegue en producción, se recomienda usar Render.com:

1. Configura un servicio web en Render apuntando al repositorio
2. Establece el comando de inicio: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Configura las variables de entorno necesarias
4. Despliega la aplicación

## Uso de IA Gemini

Para utilizar la integración con Gemini AI, necesitas:

1. Obtener una API key de Google AI Studio
2. Configurar la variable `GEMINI_API_KEY` en el archivo `.env`
3. Navegar a la sección de análisis en el dashboard

## Contribuciones

Las contribuciones son bienvenidas. Por favor, sigue estos pasos:

1. Crea un fork del repositorio
2. Crea una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Haz commit de tus cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Haz push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## Licencia

[MIT](LICENSE)

---

Desarrollado con ❤️ por [Tu Nombre]
