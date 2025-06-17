import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from .pages import home, trading, analysis, settings, analysis_lw_chart
# Importamos el nuevo componente de lightweight-charts

def create_dash_app(routes_pathname_prefix):
    """
    Crea una aplicación Dash independiente para ser montada en FastAPI
    
    Args:
        routes_pathname_prefix: El prefijo para todas las rutas Dash
        
    Returns:
        La aplicación Dash configurada
    """
    # Crear una aplicación Dash independiente (sin servidor Flask)
    app = dash.Dash(
        __name__,
        requests_pathname_prefix=routes_pathname_prefix,
        external_stylesheets=[dbc.themes.DARKLY],
        external_scripts=[
            # Script de TradingView Lightweight Charts
            "https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"
        ],
        suppress_callback_exceptions=True,
        # Importante: Permitir a Dash acceder a las cookies de FastAPI
        update_title=None,
        serve_locally=True,
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1"}
        ]
    )
    
    # Configurar el layout principal de la aplicación Dash
    app.layout = html.Div([
        # Store para almacenar datos de sesión
        dcc.Store(id='session-store', storage_type='session'),
        
        # Navbar
        create_navbar(),
        
        # Contenedor principal
        dbc.Container(
            dbc.Row(
                dbc.Col(
                    html.Div(id='page-content', className='content'),
                    width=12
                ),
                className='mt-4'
            ),
            fluid=True,
            className='pt-4 pb-4'
        ),
        
        # URL para la navegación
        dcc.Location(id='url', refresh=False)
    ])
    
    # Definir callback para la navegación entre páginas
    @app.callback(
        dash.dependencies.Output('page-content', 'children'),
        dash.dependencies.Input('url', 'pathname')
    )
    def display_page(pathname):
        """Dirige al usuario a la página correspondiente basada en la URL"""
        if pathname == routes_pathname_prefix or pathname == routes_pathname_prefix[:-1]:
            return home.layout
        elif pathname == routes_pathname_prefix + 'trading' or pathname == routes_pathname_prefix + 'trading/':
            return trading.layout
        elif pathname == routes_pathname_prefix + 'analysis' or pathname == routes_pathname_prefix + 'analysis/':
            return analysis.layout
            
        elif pathname == routes_pathname_prefix + 'analysis-lw' or pathname == routes_pathname_prefix + 'analysis-lw/':
            return analysis_lw_chart.create_analysis_lw_page()
            
        elif pathname == routes_pathname_prefix + 'settings' or pathname == routes_pathname_prefix + 'settings/':
            return settings.layout
        else:
            # Si la URL no es válida, mostrar página 404
            return html.Div([
                html.H1('404: Página no encontrada', className='text-danger'),
                html.Hr(),
                html.P(f"La página {pathname} no existe..."),
                dbc.Button("Volver al inicio", href=routes_pathname_prefix, color="primary")
            ])
    
    # Registrar callbacks de las páginas
    home.register_callbacks(app)
    trading.register_callbacks(app)
    analysis.register_callbacks(app)  # Solo mantenemos el análisis principal

    analysis_lw_chart.register_lw_chart_callbacks(app)  # Nuevo componente de lightweight-charts
    
    settings.register_callbacks(app)
    
    return app

def create_navbar():
    """Crea la barra de navegación para la aplicación Dash"""
    return dbc.Navbar(
        dbc.Container(
            [
                dbc.NavbarBrand("TradingRoad", href="/dashboard/"),
                dbc.Nav(
                    [
                        dbc.NavItem(dbc.NavLink("Trading", href="/dashboard/trading")),
                        dbc.NavItem(dbc.NavLink("Análisis", href="/dashboard/analysis")),
                        dbc.NavItem(dbc.NavLink("Configuración", href="/dashboard/settings")),
                    ],
                    className="ms-auto",
                    navbar=True
                ),
                dbc.NavbarToggler(id="navbar-toggler"),
            ]
        ),
        color="primary",
        dark=True,
        className="mb-4"
    )
