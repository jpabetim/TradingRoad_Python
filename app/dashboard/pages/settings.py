import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc

# Layout principal de la página de configuración
layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.H2("Configuración", className="text-primary"),
            html.P("Configuración de la plataforma y ajustes personales"),
            html.Hr(),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Tabs([
                # Tab de configuración general
                dbc.Tab(label="General", tab_id="general-tab", children=[
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.H4("Tema", className="mb-3"),
                                    dbc.RadioItems(
                                        id="theme-selector",
                                        options=[
                                            {"label": "Oscuro (Predeterminado)", "value": "dark"},
                                            {"label": "Claro", "value": "light"}
                                        ],
                                        value="dark",
                                        inline=False
                                    ),
                                    html.Hr(),
                                    html.H4("Moneda principal", className="mb-3"),
                                    dbc.RadioItems(
                                        id="currency-selector",
                                        options=[
                                            {"label": "USD", "value": "usd"},
                                            {"label": "EUR", "value": "eur"},
                                            {"label": "BTC", "value": "btc"}
                                        ],
                                        value="usd",
                                        inline=False
                                    ),
                                    html.Hr(),
                                    html.H4("Actualizaciones", className="mb-3"),
                                    dbc.Switch(
                                        id="auto-update-switch",
                                        label="Actualizar datos automáticamente",
                                        value=True,
                                        className="mb-2"
                                    ),
                                    dbc.FormText("Establece la frecuencia de actualización:"),
                                    dbc.RadioItems(
                                        id="update-frequency",
                                        options=[
                                            {"label": "Cada 5 segundos", "value": 5},
                                            {"label": "Cada 30 segundos", "value": 30},
                                            {"label": "Cada minuto", "value": 60},
                                            {"label": "Cada 5 minutos", "value": 300}
                                        ],
                                        value=60,
                                        inline=False,
                                        className="mt-2"
                                    ),
                                ], width=12, lg=6),
                                dbc.Col([
                                    html.H4("Panel de trading", className="mb-3"),
                                    dbc.Switch(
                                        id="confirm-orders-switch",
                                        label="Confirmar órdenes antes de enviar",
                                        value=True,
                                        className="mb-2"
                                    ),
                                    dbc.Switch(
                                        id="show-pnl-switch",
                                        label="Mostrar P&L en tiempo real",
                                        value=True,
                                        className="mb-2"
                                    ),
                                    dbc.Switch(
                                        id="sound-alerts-switch",
                                        label="Alertas sonoras para operaciones",
                                        value=False,
                                        className="mb-2"
                                    ),
                                    html.Hr(),
                                    html.H4("Notificaciones", className="mb-3"),
                                    dbc.Checklist(
                                        options=[
                                            {"label": "Órdenes ejecutadas", "value": "orders"},
                                            {"label": "Cambios significativos de precio", "value": "price"},
                                            {"label": "Señales de análisis técnico", "value": "signals"},
                                            {"label": "Alertas de análisis AI", "value": "ai"}
                                        ],
                                        value=["orders", "signals"],
                                        id="notification-checklist",
                                        switch=True
                                    ),
                                ], width=12, lg=6)
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button(
                                        "Guardar configuración",
                                        id="save-settings-button",
                                        color="primary",
                                        className="mt-4"
                                    ),
                                    html.Div(id="settings-save-result")
                                ])
                            ])
                        ])
                    ])
                ]),
                
                # Tab de conexiones de exchange
                dbc.Tab(label="Exchanges", tab_id="exchanges-tab", children=[
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.H4("Conectar exchanges", className="mb-3"),
                                    dbc.Select(
                                        id="exchange-type-selector",
                                        options=[
                                            {"label": "Binance", "value": "binance"},
                                            {"label": "BingX", "value": "bingx"},
                                            {"label": "Bybit", "value": "bybit"},
                                            {"label": "Bitget", "value": "bitget"}
                                        ],
                                        value="binance"
                                    ),
                                    html.Div([
                                        dbc.Label("API Key", html_for="api-key-input"),
                                        dbc.Input(id="api-key-input", placeholder="Ingrese su API Key", type="password")
                                    ], className="mt-3"),
                                    html.Div([
                                        dbc.Label("API Secret", html_for="api-secret-input"),
                                        dbc.Input(id="api-secret-input", placeholder="Ingrese su API Secret", type="password")
                                    ], className="mt-3"),
                                    dbc.Button(
                                        "Conectar exchange",
                                        id="connect-exchange-button",
                                        color="success",
                                        className="mt-3"
                                    ),
                                    html.Div(id="connect-exchange-result")
                                ], width=12, lg=6),
                                
                                dbc.Col([
                                    html.H4("Exchanges conectados", className="mb-3"),
                                    html.Div(id="connected-exchanges-container", children=[
                                        html.P("No hay exchanges conectados", className="text-muted")
                                    ])
                                ], width=12, lg=6)
                            ])
                        ])
                    ])
                ]),
                
                # Tab de perfil
                dbc.Tab(label="Perfil", tab_id="profile-tab", children=[
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.H4("Información de usuario", className="mb-3"),
                                    html.Div([
                                        dbc.Label("Nombre de usuario"),
                                        dbc.Input(id="username-input", value="usuario_ejemplo", disabled=True)
                                    ], className="mb-3"),
                                    html.Div([
                                        dbc.Label("Email"),
                                        dbc.Input(id="email-input", value="usuario@ejemplo.com", type="email")
                                    ], className="mb-3"),
                                    html.Div([
                                        dbc.Label("Nivel de cuenta"),
                                        dbc.Badge("Premium", color="warning", className="ms-2 p-2")
                                    ], className="mb-3"),
                                    dbc.Button(
                                        "Actualizar información",
                                        id="update-profile-button",
                                        color="primary",
                                        className="mt-2"
                                    )
                                ], width=12, lg=6),
                                
                                dbc.Col([
                                    html.H4("Cambiar contraseña", className="mb-3"),
                                    html.Div([
                                        dbc.Label("Contraseña actual"),
                                        dbc.Input(id="current-password-input", placeholder="Ingrese contraseña actual", type="password")
                                    ], className="mb-3"),
                                    html.Div([
                                        dbc.Label("Nueva contraseña"),
                                        dbc.Input(id="new-password-input", placeholder="Ingrese nueva contraseña", type="password")
                                    ], className="mb-3"),
                                    html.Div([
                                        dbc.Label("Confirmar contraseña"),
                                        dbc.Input(id="confirm-password-input", placeholder="Confirme nueva contraseña", type="password")
                                    ], className="mb-3"),
                                    dbc.Button(
                                        "Cambiar contraseña",
                                        id="change-password-button",
                                        color="primary",
                                        className="mt-2"
                                    ),
                                    html.Div(id="password-change-result")
                                ], width=12, lg=6)
                            ])
                        ])
                    ])
                ]),
                
                # Tab de API Gemini
                dbc.Tab(label="API IA", tab_id="api-tab", children=[
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.H4("Configuración de API de Gemini", className="mb-3"),
                                    html.P("Configure su API key para el análisis con inteligencia artificial."),
                                    html.Div([
                                        dbc.Label("Gemini API Key"),
                                        dbc.Input(
                                            id="gemini-api-key-input", 
                                            placeholder="Ingrese su Gemini API Key",
                                            value="AIzaSyCaijxBkHVI05Y2uYz6iU5tgxxz8oUlUok",
                                            type="password"
                                        )
                                    ], className="mb-3"),
                                    dbc.Button(
                                        "Guardar API Key",
                                        id="save-api-key-button",
                                        color="primary",
                                        className="mt-2"
                                    ),
                                    html.Div(id="api-key-save-result")
                                ], width=12)
                            ])
                        ])
                    ])
                ])
            ], id="settings-tabs")
        ], width=12)
    ])
])

def register_callbacks(app):
    """Registrar los callbacks para la página de configuración"""
    
    @app.callback(
        Output("settings-save-result", "children"),
        Input("save-settings-button", "n_clicks"),
        State("theme-selector", "value"),
        State("currency-selector", "value"),
        State("auto-update-switch", "value"),
        State("update-frequency", "value"),
        State("notification-checklist", "value"),
        prevent_initial_call=True
    )
    def save_settings(n_clicks, theme, currency, auto_update, frequency, notifications):
        """Guarda la configuración general"""
        # Aquí se guardarían los ajustes en la base de datos o localStorage
        return dbc.Alert(
            "Configuración guardada correctamente",
            color="success",
            duration=4000,  # Desaparece después de 4 segundos
            is_open=True,
            className="mt-3"
        )
    
    @app.callback(
        Output("connect-exchange-result", "children"),
        Input("connect-exchange-button", "n_clicks"),
        State("exchange-type-selector", "value"),
        State("api-key-input", "value"),
        State("api-secret-input", "value"),
        prevent_initial_call=True
    )
    def connect_exchange(n_clicks, exchange, api_key, api_secret):
        """Conecta un nuevo exchange"""
        # Aquí se conectaría con el exchange seleccionado
        if not api_key or not api_secret:
            return dbc.Alert(
                "Por favor, ingrese tanto API Key como API Secret",
                color="danger",
                className="mt-3"
            )
        
        # Simular conexión exitosa
        return dbc.Alert(
            f"Exchange {exchange} conectado correctamente",
            color="success",
            duration=4000,
            is_open=True,
            className="mt-3"
        )
    
    @app.callback(
        Output("password-change-result", "children"),
        Input("change-password-button", "n_clicks"),
        State("current-password-input", "value"),
        State("new-password-input", "value"),
        State("confirm-password-input", "value"),
        prevent_initial_call=True
    )
    def change_password(n_clicks, current_pwd, new_pwd, confirm_pwd):
        """Cambia la contraseña del usuario"""
        # Aquí se validaría y cambiaría la contraseña
        if not current_pwd or not new_pwd or not confirm_pwd:
            return dbc.Alert(
                "Por favor, complete todos los campos",
                color="danger",
                className="mt-3"
            )
        
        if new_pwd != confirm_pwd:
            return dbc.Alert(
                "Las contraseñas nuevas no coinciden",
                color="danger",
                className="mt-3"
            )
        
        # Simular éxito
        return dbc.Alert(
            "Contraseña cambiada correctamente",
            color="success",
            duration=4000,
            is_open=True,
            className="mt-3"
        )
    
    @app.callback(
        Output("api-key-save-result", "children"),
        Input("save-api-key-button", "n_clicks"),
        State("gemini-api-key-input", "value"),
        prevent_initial_call=True
    )
    def save_api_key(n_clicks, api_key):
        """Guarda la API key de Gemini"""
        # Aquí se guardaría la API key
        if not api_key:
            return dbc.Alert(
                "Por favor, ingrese una API Key válida",
                color="danger",
                className="mt-3"
            )
        
        # Simular éxito
        return dbc.Alert(
            "API Key de Gemini guardada correctamente",
            color="success",
            duration=4000,
            is_open=True,
            className="mt-3"
        )
