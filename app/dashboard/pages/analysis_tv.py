import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

# Layout principal con widget de TradingView embebido
def layout():
    return html.Div([
        # Navbar superior con título y controles básicos
        dbc.Navbar(
            dbc.Container([
                html.A(
                    dbc.Row([
                        dbc.Col(html.Img(src="/assets/logo.png", height="30px", className="me-2")),
                        dbc.Col(dbc.NavbarBrand("TradeRoad", className="ms-2 text-light")),
                    ], align="center"),
                    href="/",
                    style={"textDecoration": "none"},
                ),
                dbc.Row([
                    dbc.Col([
                        dbc.Button("Show Panel", id="toggle-panel-button", color="secondary", size="sm"),
                        dbc.Button("Light Mode", id="toggle-theme-button", color="secondary", size="sm", className="ms-2"),
                    ]),
                ], className="ms-auto flex-nowrap align-items-center"),
            ], fluid=True),
            color="dark",
            dark=True,
        ),
        
        # Contenedor principal con panel lateral y gráfico
        dbc.Container([
            dbc.Row([
                # Panel lateral de controles (inicialmente visible)
                dbc.Col([
                    html.Div([
                        # Título del panel
                        html.H5("Market Controls", className="text-info mb-3"),
                        
                        # Selector de fuente de datos
                        html.Label("Data Source", className="text-light mt-3"),
                        dbc.Select(
                            id="exchange-selector",
                            options=[
                                {"label": "Binance Futures", "value": "binance_futures"},
                                {"label": "Binance Spot", "value": "binance_spot"},
                                {"label": "Bybit", "value": "bybit"},
                                {"label": "OKX", "value": "okx"},
                            ],
                            value="binance_futures",
                            className="mb-3",
                        ),
                        
                        # Selector de par/símbolo
                        html.Label("Trading Pair / Symbol", className="text-light"),
                        dbc.Input(
                            id="pair-input",
                            type="text",
                            value="ETHUSDT",
                            placeholder="Enter symbol...",
                            className="mb-3",
                        ),
                        
                        # Botones de temporalidad
                        html.Label("Timeframe", className="text-light"),
                        dbc.ButtonGroup(
                            [
                                dbc.Button("1M", id="tf-1m", outline=True, color="secondary", size="sm"),
                                dbc.Button("5M", id="tf-5m", outline=True, color="secondary", size="sm"),
                                dbc.Button("15M", id="tf-15m", outline=True, color="secondary", size="sm"),
                                dbc.Button("1H", id="tf-1h", outline=True, color="primary", size="sm"),
                                dbc.Button("4H", id="tf-4h", outline=True, color="secondary", size="sm"),
                                dbc.Button("1D", id="tf-1d", outline=True, color="secondary", size="sm"),
                                dbc.Button("1W", id="tf-1w", outline=True, color="secondary", size="sm"),
                            ],
                            className="mb-3 d-flex flex-wrap",
                        ),
                        
                        # Botones de análisis IA
                        dbc.Row([
                            dbc.Col(
                                dbc.Button("Hide AI Drawings", id="toggle-ai-drawings", color="success", size="sm", className="w-100")
                            ),
                            dbc.Col(
                                dbc.Button("Analyze (AI)", id="analyze-button", color="info", size="sm", className="w-100")
                            ),
                        ], className="mb-3"),
                        
                        # Configuración de visualización
                        html.Div([
                            html.H6("Display Settings", className="text-light d-flex justify-content-between align-items-center"),
                            dbc.Button("Show", id="toggle-display-settings", color="link", size="sm", className="p-0"),
                        ], className="d-flex justify-content-between align-items-center mb-2"),
                        
                        # Sección de resultados del análisis IA
                        html.Div([
                            html.H5("AI Analysis Results", className="text-info mt-4 mb-3"),
                            
                            # Escenario principal
                            html.H6("Primary Scenario", className="text-light"),
                            html.Div([
                                html.P("Escenario Principal: Rebote desde Demanda/Fib 61.8-70.5%", 
                                      className="fw-bold mb-2"),
                                html.P([
                                    "El precio se encuentra en una zona de confluencia significativa (Fib 61.8-70.5% + OB + nivel de soporte. Se espera un posible rebote de continuación (patrón simple trade sin señal de confirmación) hacia zona más alta donde podría reflejar resistencias (POI 1H en 2600) o testear la oferta en 2612-2730, formando un posible HL."
                                ], className="small text-muted mb-2"),
                                html.P([
                                    "Proyección: Ruptura con varias y cierre de vela de 1H/4H por debajo de 2540 invalidaría temporalmente el escenario alcista a corto plazo y abriría la posibilidad hacia nuevos mínimos."
                                ], className="small text-muted")
                            ], className="mb-3"),
                            
                            # Setup asociado
                            html.Div([
                                html.P("Associated Setup: LARGO", className="mb-1"),
                                html.Ul([
                                    html.Li(["Type: LARGO"], className="small text-muted"),
                                    html.Li([
                                        "Entry Condition: Buscar confirmación alcista (ChoCh en 15M/5M, vela de rechazo con volumen) en la zona de demanda 2500-2525. La entrada puede ser agresiva al entrar en la zona o más conservadora esperando confirmación LTF (1M pattern)."
                                    ], className="small text-muted"),
                                    html.Li(["Ideal Entry Price: 2520.00"], className="small text-muted"),
                                    html.Li(["Entry Zone: [2500.00 - 2525.00]"], className="small text-muted"),
                                    html.Li(["Stop Loss: 2475.00"], className="small text-muted"),
                                    html.Li(["Take Profit: 2630.00"], className="small text-muted"),
                                ], className="ps-3 mb-0")
                            ])
                        ], className="analysis-results")
                        
                    ], className="p-3 h-100"),
                ], id="side-panel", width=3, className="bg-dark", style={"height": "calc(100vh - 56px)", "overflowY": "auto"}),
                
                # Columna principal para el widget de TradingView (ocupa todo el espacio disponible)
                dbc.Col([
                    html.Div([
                        # TradingView Widget
                        html.Div([
                            html.Iframe(
                                id='tradingview-widget',
                                src="",  # Se actualizará con JavaScript
                                style={
                                    'width': '100%',
                                    'height': 'calc(100vh - 56px)',
                                    'border': 'none',
                                }
                            ),
                        ], id="chart-container", style={'height': 'calc(100vh - 56px)'}),
                        
                        # Script para inicializar el widget cuando cambie la fuente de datos/símbolo
                        html.Script(id='tradingview-script'),
                    ])
                ], id="chart-col", width=9),
            ], className="g-0"),  # Sin gutters para maximizar espacio
        ], fluid=True, className="px-0"),
        
        # Componentes ocultos para manejar estado
        dcc.Store(id="current-symbol", data="ETHUSDT"),
        dcc.Store(id="current-exchange", data="binance_futures"),
        dcc.Store(id="current-interval", data="60"),  # 1H por defecto
        
        # JavaScript para controlar el widget de TradingView
        html.Script("""
            function updateTradingViewWidget(symbol, exchange, interval) {
                // Remover widget anterior si existe
                const container = document.getElementById('chart-container');
                while (container.firstChild) {
                    container.removeChild(container.firstChild);
                }
                
                // Crear nuevo widget
                const iframe = document.createElement('iframe');
                iframe.id = 'tradingview-widget';
                iframe.style.width = '100%';
                iframe.style.height = 'calc(100vh - 56px)';
                iframe.style.border = 'none';
                
                // Mapear exchanges a identificadores de TradingView
                let tvExchange = 'BINANCE';
                if (exchange === 'binance_futures') tvExchange = 'BINANCEUSDM';
                else if (exchange === 'bybit') tvExchange = 'BYBIT';
                else if (exchange === 'okx') tvExchange = 'OKX';
                
                // Crear URL del widget avanzado
                iframe.src = `https://www.tradingview.com/widgetembed/?frameElementId=tradingview-widget&symbol=${tvExchange}:${symbol}&interval=${interval}&hideideas=1&theme=dark&style=1&timezone=exchange&withdateranges=1&studies=[]&hideideasbutton=1&enablepublishing=0&showpopupbutton=1&showflyover=1`;
                
                container.appendChild(iframe);
            }
            
            // Inicializar con valores por defecto
            setTimeout(function() {
                updateTradingViewWidget('ETHUSDT', 'binance_futures', '60');
            }, 500);
        """, id="tradingview-control-script"),
    ])

# Registrar callbacks
def register_callbacks(app):
    # Callback para actualizar el widget de TradingView cuando cambia el símbolo o exchange
    @app.callback(
        Output('tradingview-script', 'children'),
        [Input('pair-input', 'value'),
         Input('exchange-selector', 'value'),
         Input('tf-1m', 'n_clicks'),
         Input('tf-5m', 'n_clicks'),
         Input('tf-15m', 'n_clicks'),
         Input('tf-1h', 'n_clicks'),
         Input('tf-4h', 'n_clicks'),
         Input('tf-1d', 'n_clicks'),
         Input('tf-1w', 'n_clicks')],
        [State('current-symbol', 'data'),
         State('current-exchange', 'data'),
         State('current-interval', 'data')]
    )
    def update_tradingview_widget(symbol, exchange, 
                                  n1, n5, n15, n1h, n4h, n1d, n1w,
                                  current_symbol, current_exchange, current_interval):
        ctx = dash.callback_context
        
        # Determinar qué input desencadenó el callback
        if not ctx.triggered:
            # Primera carga, usar valores predeterminados
            interval = current_interval
        else:
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            # Actualizar intervalo si se presionó un botón de temporalidad
            if trigger_id == 'tf-1m':
                interval = '1'
            elif trigger_id == 'tf-5m':
                interval = '5'
            elif trigger_id == 'tf-15m':
                interval = '15'
            elif trigger_id == 'tf-1h':
                interval = '60'
            elif trigger_id == 'tf-4h':
                interval = '240'
            elif trigger_id == 'tf-1d':
                interval = 'D'
            elif trigger_id == 'tf-1w':
                interval = 'W'
            else:
                # Si no se presionó ningún botón de temporalidad, mantener el intervalo actual
                interval = current_interval
        
        # Si hay cambios en los parámetros, actualizar el widget
        if symbol != current_symbol or exchange != current_exchange or interval != current_interval:
            return f"""
                updateTradingViewWidget('{symbol}', '{exchange}', '{interval}');
            """
        
        # Si no hay cambios, no hacer nada
        raise PreventUpdate

    # Callback para actualizar los almacenes de datos
    @app.callback(
        [Output('current-symbol', 'data'),
         Output('current-exchange', 'data'),
         Output('current-interval', 'data')],
        [Input('pair-input', 'value'),
         Input('exchange-selector', 'value'),
         Input('tf-1m', 'n_clicks'),
         Input('tf-5m', 'n_clicks'),
         Input('tf-15m', 'n_clicks'),
         Input('tf-1h', 'n_clicks'),
         Input('tf-4h', 'n_clicks'),
         Input('tf-1d', 'n_clicks'),
         Input('tf-1w', 'n_clicks')],
        [State('current-symbol', 'data'),
         State('current-exchange', 'data'),
         State('current-interval', 'data')]
    )
    def update_stores(symbol, exchange, 
                      n1, n5, n15, n1h, n4h, n1d, n1w,
                      current_symbol, current_exchange, current_interval):
        ctx = dash.callback_context
        
        # Determinar qué input desencadenó el callback
        if not ctx.triggered:
            # Primera carga, devolver valores actuales
            return current_symbol, current_exchange, current_interval
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Actualizar intervalo si se presionó un botón de temporalidad
        if trigger_id == 'tf-1m':
            interval = '1'
        elif trigger_id == 'tf-5m':
            interval = '5'
        elif trigger_id == 'tf-15m':
            interval = '15'
        elif trigger_id == 'tf-1h':
            interval = '60'
        elif trigger_id == 'tf-4h':
            interval = '240'
        elif trigger_id == 'tf-1d':
            interval = 'D'
        elif trigger_id == 'tf-1w':
            interval = 'W'
        else:
            # Si no se presionó ningún botón de temporalidad, mantener el intervalo actual
            interval = current_interval
        
        # Devolver los valores actualizados
        return symbol, exchange, interval

    # Callback para mostrar/ocultar el panel lateral
    @app.callback(
        [Output('side-panel', 'width'),
         Output('chart-col', 'width'),
         Output('toggle-panel-button', 'children')],
        [Input('toggle-panel-button', 'n_clicks')],
        [State('side-panel', 'width')]
    )
    def toggle_sidebar(n_clicks, current_width):
        if n_clicks is None:
            # Primera carga, panel visible
            return 3, 9, "Hide Panel"
        
        if current_width == 3:
            # Ocultar panel
            return 0, 12, "Show Panel"
        else:
            # Mostrar panel
            return 3, 9, "Hide Panel"

    # Callback para activar análisis IA
    @app.callback(
        Output('analyze-button', 'color'),
        [Input('analyze-button', 'n_clicks')]
    )
    def run_ai_analysis(n_clicks):
        if n_clicks is None:
            raise PreventUpdate
        
        # Aquí iría la lógica para ejecutar el análisis IA
        # Por ahora simplemente cambiamos el color del botón
        return "success"
