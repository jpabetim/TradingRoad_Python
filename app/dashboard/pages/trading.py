import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Layout principal de la página de trading
layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.H2("Trading en Tiempo Real", className="text-primary"),
            html.P("Conecte con exchanges y realice operaciones de trading"),
            html.Hr(),
        ], width=12)
    ]),
    
    dbc.Row([
        # Panel de selección de exchange y par
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Configuración", className="card-title")),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Exchange"),
                            dcc.Dropdown(
                                id="exchange-selector",
                                options=[
                                    {"label": "Binance", "value": "binance"},
                                    {"label": "BingX", "value": "bingx"},
                                    {"label": "Bitget", "value": "bitget"},
                                    {"label": "Bybit", "value": "bybit"}
                                ],
                                value="binance",
                                clearable=False
                            )
                        ], width=6),
                        dbc.Col([
                            html.Label("Par de trading"),
                            dcc.Dropdown(
                                id="pair-selector",
                                options=[
                                    {"label": "BTC/USDT", "value": "BTC/USDT"},
                                    {"label": "ETH/USDT", "value": "ETH/USDT"},
                                    {"label": "XRP/USDT", "value": "XRP/USDT"},
                                    {"label": "SOL/USDT", "value": "SOL/USDT"}
                                ],
                                value="BTC/USDT",
                                clearable=False
                            )
                        ], width=6),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Timeframe"),
                            dcc.Dropdown(
                                id="timeframe-selector",
                                options=[
                                    {"label": "1 minuto", "value": "1m"},
                                    {"label": "5 minutos", "value": "5m"},
                                    {"label": "15 minutos", "value": "15m"},
                                    {"label": "1 hora", "value": "1h"},
                                    {"label": "4 horas", "value": "4h"},
                                    {"label": "1 día", "value": "1d"},
                                ],
                                value="15m",
                                clearable=False
                            )
                        ], width=6),
                        dbc.Col([
                            html.Div([
                                html.Label("Actualización en tiempo real"),
                                html.Br(),
                                dbc.Switch(
                                    id="realtime-switch",
                                    value=True,
                                    label="Activado",
                                    className="mt-1"
                                )
                            ])
                        ], width=6)
                    ], className="mt-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button(
                                "Cargar datos",
                                id="load-data-button",
                                color="primary",
                                className="mt-3"
                            )
                        ])
                    ])
                ])
            ]),
        ], width=12, className="mb-4")
    ]),
    
    dbc.Row([
        # Gráfico de velas
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Gráfico de precio", className="card-title")),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Indicadores"),
                            dbc.Checklist(
                                options=[
                                    {"label": "Media Móvil Simple (SMA)", "value": "sma"},
                                    {"label": "Media Móvil Exponencial (EMA)", "value": "ema"},
                                    {"label": "Bandas de Bollinger", "value": "bollinger"},
                                    {"label": "RSI", "value": "rsi"}
                                ],
                                value=["sma"],
                                id="indicators-checklist",
                                inline=True,
                                switch=True
                            )
                        ], width=12)
                    ]),
                    dcc.Loading(
                        id="loading-chart",
                        type="default",
                        children=[
                            dcc.Graph(
                                id="trading-chart",
                                figure=create_empty_chart(),
                                style={"height": "60vh"}
                            )
                        ]
                    )
                ])
            ]),
        ], width=12, className="mb-4")
    ]),
    
    dbc.Row([
        # Panel de órdenes
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Panel de órdenes", className="card-title")),
                dbc.CardBody([
                    dbc.Tabs([
                        dbc.Tab(label="Mercado", tab_id="market-tab", children=[
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Tipo"),
                                    dbc.RadioItems(
                                        options=[
                                            {"label": "Compra", "value": "buy"},
                                            {"label": "Venta", "value": "sell"}
                                        ],
                                        value="buy",
                                        id="market-type",
                                        inline=True
                                    )
                                ], width=6),
                                dbc.Col([
                                    html.Label("Cantidad"),
                                    dbc.Input(
                                        id="market-amount",
                                        type="number",
                                        placeholder="Cantidad"
                                    )
                                ], width=6)
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button(
                                        "Enviar orden de mercado",
                                        id="market-order-button",
                                        color="success",
                                        className="w-100"
                                    )
                                ])
                            ])
                        ]),
                        dbc.Tab(label="Límite", tab_id="limit-tab", children=[
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Tipo"),
                                    dbc.RadioItems(
                                        options=[
                                            {"label": "Compra", "value": "buy"},
                                            {"label": "Venta", "value": "sell"}
                                        ],
                                        value="buy",
                                        id="limit-type",
                                        inline=True
                                    )
                                ], width=6),
                                dbc.Col([
                                    html.Label("Cantidad"),
                                    dbc.Input(
                                        id="limit-amount",
                                        type="number",
                                        placeholder="Cantidad"
                                    )
                                ], width=6)
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Precio"),
                                    dbc.Input(
                                        id="limit-price",
                                        type="number",
                                        placeholder="Precio límite"
                                    )
                                ])
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button(
                                        "Enviar orden límite",
                                        id="limit-order-button",
                                        color="primary",
                                        className="w-100"
                                    )
                                ])
                            ])
                        ])
                    ], id="order-tabs")
                ])
            ])
        ], width=12, lg=6, className="mb-4"),
        
        # Panel de posiciones abiertas
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Posiciones abiertas", className="card-title")),
                dbc.CardBody([
                    html.Div(id="positions-container")
                ])
            ])
        ], width=12, lg=6, className="mb-4")
    ])
])

def create_empty_chart():
    """Crear un gráfico vacío para mostrar inicialmente"""
    fig = go.Figure()
    
    fig.update_layout(
        title="Seleccione un par y haga clic en 'Cargar datos'",
        xaxis_title="Fecha/Hora",
        yaxis_title="Precio",
        template="plotly_dark",
        height=600,
        showlegend=True
    )
    
    return fig

def register_callbacks(app):
    """Registrar los callbacks para la página de trading"""
    
    @app.callback(
        Output("trading-chart", "figure"),
        Input("load-data-button", "n_clicks"),
        State("exchange-selector", "value"),
        State("pair-selector", "value"),
        State("timeframe-selector", "value"),
        State("indicators-checklist", "value"),
        prevent_initial_call=True
    )
    def update_trading_chart(n_clicks, exchange, pair, timeframe, indicators):
        """Actualiza el gráfico de trading con los datos seleccionados"""
        # Aquí normalmente obtendríamos datos reales del exchange
        # Por ahora generamos datos de ejemplo
        
        dates = pd.date_range(
            end=datetime.now(), 
            periods=100, 
            freq='15min' if timeframe == '15m' else '1h'
        )
        
        # Generar datos de ejemplo para un gráfico de velas
        np.random.seed(42)
        close = 100 + np.cumsum(np.random.randn(100) * 2)
        open = close - np.random.randn(100) * 1.5
        high = np.maximum(close, open) + np.random.rand(100) * 3
        low = np.minimum(close, open) - np.random.rand(100) * 3
        volume = np.random.rand(100) * 100
        
        # Crear figura con Plotly
        fig = go.Figure()
        
        # Añadir gráfico de velas
        fig.add_trace(
            go.Candlestick(
                x=dates,
                open=open, 
                high=high,
                low=low, 
                close=close,
                name=pair
            )
        )
        
        # Añadir indicadores si están seleccionados
        if "sma" in indicators:
            sma_20 = pd.Series(close).rolling(window=20).mean()
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=sma_20,
                    name="SMA(20)",
                    line=dict(color='orange', width=1)
                )
            )
        
        if "ema" in indicators:
            ema_20 = pd.Series(close).ewm(span=20, adjust=False).mean()
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=ema_20,
                    name="EMA(20)",
                    line=dict(color='purple', width=1)
                )
            )
        
        if "bollinger" in indicators:
            sma_20 = pd.Series(close).rolling(window=20).mean()
            std_20 = pd.Series(close).rolling(window=20).std()
            upper_band = sma_20 + 2 * std_20
            lower_band = sma_20 - 2 * std_20
            
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=upper_band,
                    name="Upper Band",
                    line=dict(color='rgba(250, 0, 0, 0.5)', width=1)
                )
            )
            
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=lower_band,
                    name="Lower Band",
                    fill='tonexty',
                    fillcolor='rgba(173, 216, 230, 0.2)',
                    line=dict(color='rgba(250, 0, 0, 0.5)', width=1)
                )
            )
        
        # Actualizar layout
        fig.update_layout(
            title=f"{pair} - {timeframe} - {exchange.capitalize()}",
            xaxis_title="Fecha/Hora",
            yaxis_title="Precio",
            template="plotly_dark",
            height=600,
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        if "rsi" in indicators:
            # Crear un subplot secundario para el RSI
            fig = make_subplots(rows=2, cols=1, 
                              row_heights=[0.7, 0.3],
                              vertical_spacing=0.1,
                              shared_xaxes=True)
            
            # Añadir gráfico de velas al subplot principal
            fig.add_trace(
                go.Candlestick(
                    x=dates,
                    open=open, 
                    high=high,
                    low=low, 
                    close=close,
                    name=pair
                ),
                row=1, col=1
            )
            
            # Calcular RSI
            delta = pd.Series(close).diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # Añadir RSI al subplot inferior
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=rsi,
                    name="RSI(14)",
                    line=dict(color='cyan', width=1)
                ),
                row=2, col=1
            )
            
            # Añadir líneas de referencia para RSI
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
            
            # Actualizar layout
            fig.update_layout(
                title=f"{pair} - {timeframe} - {exchange.capitalize()}",
                xaxis_title="Fecha/Hora",
                template="plotly_dark",
                height=800,
                showlegend=True,
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                )
            )
            
            # Actualizar ejes
            fig.update_yaxes(title_text="Precio", row=1, col=1)
            fig.update_yaxes(title_text="RSI", row=2, col=1)
        
        return fig
    
    @app.callback(
        Output("positions-container", "children"),
        Input("exchange-selector", "value")
    )
    def update_positions(exchange):
        """Actualiza la tabla de posiciones abiertas"""
        # Simulamos algunas posiciones abiertas
        positions = [
            {"symbol": "BTC/USDT", "type": "Long", "entry": "43,125.45", "current": "43,562.45", "pnl": "+1.2%", "color": "success"},
            {"symbol": "ETH/USDT", "type": "Short", "entry": "2,400.00", "current": "2,345.67", "pnl": "+2.3%", "color": "success"}
        ] if exchange in ["binance", "bingx"] else []
        
        if not positions:
            return html.P("No hay posiciones abiertas en este exchange.")
        
        # Crear un componente para mostrar los datos
        positions_table = html.Div([
            html.Table([
                html.Thead(
                    html.Tr([
                        html.Th("Par"),
                        html.Th("Tipo"),
                        html.Th("Entrada"),
                        html.Th("Actual"),
                        html.Th("P&L")
                    ])
                ),
                html.Tbody([
                    html.Tr([
                        html.Td(position["symbol"]),
                        html.Td(position["type"]),
                        html.Td(position["entry"]),
                        html.Td(position["current"]),
                        html.Td(position["pnl"], className=f"text-{position['color']}")
                    ]) for position in positions
                ])
            ], className="table table-striped table-hover")
        ])
        
        return positions_table
