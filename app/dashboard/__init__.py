import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from .pages import home, trading, analysis, settings

def create_dash_app(server, routes_pathname_prefix):
    """
    Crea una aplicación Dash integrada con FastAPI
    
    Args:
        server: La instancia de FastAPI
        routes_pathname_prefix: El prefijo para todas las rutas Dash
        
    Returns:
        La aplicación Dash configurada
    """
    app = dash.Dash(
        __name__,
        server=server,
        routes_pathname_prefix=routes_pathname_prefix,
        external_stylesheets=[dbc.themes.DARKLY],
        suppress_callback_exceptions=True,
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
        if pathname == routes_pathname_prefix:
            return home.layout
        elif pathname == routes_pathname_prefix + 'trading':
            return trading.layout
        elif pathname == routes_pathname_prefix + 'analysis':
            return analysis.layout
        elif pathname == routes_pathname_prefix + 'settings':
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
    analysis.register_callbacks(app)
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
