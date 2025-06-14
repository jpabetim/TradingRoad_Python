import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_empty_chart(analysis_type):
    """Crear un gráfico vacío para mostrar inicialmente"""
    fig = go.Figure()
    
    fig.update_layout(
        title=f"Seleccione un activo y periodo para ver el análisis {analysis_type}",
        xaxis_title="Fecha",
        yaxis_title="Valor",
        template="plotly_dark",
        height=400
    )
    
    return fig

# Layout principal de la página de análisis
layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.H2("Análisis de Mercado", className="text-primary"),
            html.P("Análisis técnico y con inteligencia artificial"),
            html.Hr(),
        ], width=12)
    ]),
    
    dbc.Row([
        # Panel de selección de activo y periodo
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Seleccionar activo y periodo", className="card-title")),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Seleccionar activo"),
                            dcc.Dropdown(
                                id="asset-selector",
                                options=[
                                    {"label": "Bitcoin (BTC/USDT)", "value": "BTC/USDT"},
                                    {"label": "Ethereum (ETH/USDT)", "value": "ETH/USDT"},
                                    {"label": "Binance Coin (BNB/USDT)", "value": "BNB/USDT"},
                                    {"label": "Ripple (XRP/USDT)", "value": "XRP/USDT"},
                                ],
                                value="BTC/USDT",
                                clearable=False
                            )
                        ], width=6),
                        dbc.Col([
                            html.Label("Periodo"),
                            dcc.Dropdown(
                                id="period-selector",
                                options=[
                                    {"label": "1 día", "value": "1d"},
                                    {"label": "1 semana", "value": "1w"},
                                    {"label": "1 mes", "value": "1m"},
                                    {"label": "3 meses", "value": "3m"},
                                    {"label": "6 meses", "value": "6m"},
                                    {"label": "1 año", "value": "1y"},
                                ],
                                value="1m",
                                clearable=False
                            )
                        ], width=6),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button(
                                "Analizar",
                                id="analyze-button",
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
        # Panel de análisis técnico
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Análisis Técnico", className="card-title")),
                dbc.CardBody([
                    dcc.Loading(
                        id="loading-technical-analysis",
                        type="default",
                        children=[
                            dcc.Graph(
                                id="technical-analysis-chart",
                                figure=create_empty_chart("técnico"),
                                style={"height": "50vh"}
                            )
                        ]
                    )
                ])
            ]),
        ], width=12, lg=6, className="mb-4"),
        
        # Panel de análisis de volatilidad
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Análisis de Volatilidad", className="card-title")),
                dbc.CardBody([
                    dcc.Loading(
                        id="loading-volatility-analysis",
                        type="default",
                        children=[
                            dcc.Graph(
                                id="volatility-analysis-chart",
                                figure=create_empty_chart("volatilidad"),
                                style={"height": "50vh"}
                            )
                        ]
                    )
                ])
            ]),
        ], width=12, lg=6, className="mb-4"),
    ]),
    
    dbc.Row([
        # Panel de análisis AI
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Análisis con IA (Gemini AI)", className="card-title")),
                dbc.CardBody([
                    dbc.Spinner(
                        dbc.Alert(
                            "Pulse el botón 'Analizar' para obtener un análisis de IA con Gemini",
                            id="ai-analysis-results",
                            color="info",
                            style={"white-space": "pre-line"}
                        )
                    ),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button(
                                "Generar análisis con IA",
                                id="generate-ai-analysis",
                                color="success",
                                className="mt-3"
                            )
                        ])
                    ])
                ])
            ]),
        ], width=12, className="mb-4")
    ]),
    
    dbc.Row([
        # Panel de correlación
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Correlación entre activos", className="card-title")),
                dbc.CardBody([
                    dcc.Loading(
                        id="loading-correlation",
                        type="default",
                        children=[
                            dcc.Graph(
                                id="correlation-heatmap",
                                figure=create_correlation_heatmap(),
                                style={"height": "40vh"}
                            )
                        ]
                    )
                ])
            ]),
        ], width=12, className="mb-4")
    ])
])

def create_correlation_heatmap():
    """Crear un heatmap de correlación entre varios activos"""
    # Crear datos de ejemplo para correlación
    np.random.seed(42)
    assets = ["BTC", "ETH", "BNB", "XRP", "ADA", "SOL", "DOT"]
    n_assets = len(assets)
    
    # Crear una matriz de correlación aleatoria pero realista
    base = np.random.rand(n_assets, n_assets)
    corr = (base + base.T) / 2  # Hacer simétrica
    np.fill_diagonal(corr, 1)  # Diagonal de 1's
    
    # Asegurar que los valores estén entre -1 y 1, con tendencia a valores positivos para criptomonedas
    corr = (corr * 1.2) - 0.2
    corr = np.clip(corr, -1, 1)
    
    # Crear figura de heatmap
    fig = px.imshow(
        corr,
        x=assets,
        y=assets,
        color_continuous_scale="RdBu_r",
        labels=dict(x="Activo", y="Activo", color="Correlación")
    )
    
    fig.update_layout(
        title="Correlación entre principales criptomonedas (últimos 30 días)",
        template="plotly_dark",
        height=400
    )
    
    return fig

def register_callbacks(app):
    """Registrar los callbacks para la página de análisis"""
    
    @app.callback(
        Output("technical-analysis-chart", "figure"),
        Output("volatility-analysis-chart", "figure"),
        Input("analyze-button", "n_clicks"),
        State("asset-selector", "value"),
        State("period-selector", "value"),
        prevent_initial_call=True
    )
    def update_analysis_charts(n_clicks, asset, period):
        """Actualiza los gráficos de análisis técnico y volatilidad"""
        # Determinar el número de días basado en el periodo seleccionado
        period_days = {
            "1d": 1,
            "1w": 7,
            "1m": 30,
            "3m": 90,
            "6m": 180,
            "1y": 365
        }
        days = period_days.get(period, 30)
        
        # Generar fechas para el período seleccionado
        dates = pd.date_range(
            end=datetime.now(), 
            periods=days, 
            freq='D'
        )
        
        # Generar datos de precio de ejemplo
        np.random.seed(42)
        close = 100 + np.cumsum(np.random.randn(days) * 2)
        
        # Crear gráfico de análisis técnico
        tech_fig = go.Figure()
        
        # Línea de precio
        tech_fig.add_trace(
            go.Scatter(
                x=dates,
                y=close,
                name=asset,
                line=dict(color='rgb(49, 130, 189)', width=2)
            )
        )
        
        # Añadir media móvil de 20 días
        sma_20 = pd.Series(close).rolling(window=min(20, days)).mean()
        tech_fig.add_trace(
            go.Scatter(
                x=dates,
                y=sma_20,
                name="SMA(20)",
                line=dict(color='orange', width=1.5, dash='dot')
            )
        )
        
        # Añadir media móvil de 50 días si el periodo es suficiente
        if days >= 50:
            sma_50 = pd.Series(close).rolling(window=50).mean()
            tech_fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=sma_50,
                    name="SMA(50)",
                    line=dict(color='red', width=1.5, dash='dot')
                )
            )
        
        tech_fig.update_layout(
            title=f"Análisis Técnico - {asset} - {period}",
            xaxis_title="Fecha",
            yaxis_title="Precio",
            template="plotly_dark",
            height=400,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        # Crear gráfico de análisis de volatilidad
        # Calcular volatilidad como % de cambio diario
        daily_returns = pd.Series(close).pct_change() * 100
        vol_rolling = daily_returns.rolling(window=min(20, days)).std() * np.sqrt(252)  # Volatilidad anualizada
        
        vol_fig = go.Figure()
        
        vol_fig.add_trace(
            go.Scatter(
                x=dates,
                y=vol_rolling,
                name="Volatilidad",
                fill='tozeroy',
                fillcolor='rgba(0, 176, 246, 0.2)',
                line=dict(color='rgb(0, 176, 246)', width=2)
            )
        )
        
        vol_fig.update_layout(
            title=f"Volatilidad - {asset} - {period}",
            xaxis_title="Fecha",
            yaxis_title="Volatilidad Anualizada (%)",
            template="plotly_dark",
            height=400
        )
        
        return tech_fig, vol_fig
    
    @app.callback(
        Output("ai-analysis-results", "children"),
        Output("ai-analysis-results", "color"),
        Input("generate-ai-analysis", "n_clicks"),
        State("asset-selector", "value"),
        State("period-selector", "value"),
        prevent_initial_call=True
    )
    def generate_ai_analysis(n_clicks, asset, period):
        """Genera un análisis con IA usando Gemini (simulado)"""
        # Aquí se integraría con la API de Gemini
        # Por ahora mostramos un ejemplo de análisis
        
        asset_name = asset.split('/')[0]
        
        # Simular diversos escenarios de análisis
        if asset_name == "BTC":
            analysis = f"""Análisis de {asset_name} para el período de {period}:

1. Tendencia: Alcista con resistencia en los $45,000. La media móvil de 50 días ha cruzado por encima de la media móvil de 200 días, lo que históricamente ha sido una señal alcista fuerte.

2. Volumen: Ha aumentado significativamente en las últimas sesiones, lo que confirma el interés comprador.

3. Sentimiento: Positivo según análisis de redes sociales y noticias.

4. Riesgos: Regulación gubernamental en mercados importantes puede crear volatilidad a corto plazo.

5. Recomendación: Mantener posición con stop loss en $38,500. Considerar añadir en retrocesos hacia $40,000."""
            color = "success"
        
        elif asset_name == "ETH":
            analysis = f"""Análisis de {asset_name} para el período de {period}:

1. Tendencia: Consolidación lateral después de romper resistencia de $2,200.

2. Factores técnicos: RSI en zona neutral (55), sin señales claras de sobrecompra.

3. Observaciones fundamentales: La actualización EIP-3675 podría ser catalizador positivo en próximos meses.

4. Correlación: Moviéndose más independientemente de BTC en comparación con períodos anteriores.

5. Recomendación: Posición neutral, esperar confirmación de ruptura de $2,600 para entrar largo."""
            color = "info"
            
        else:
            analysis = f"""Análisis de {asset_name} para el período de {period}:

1. Tendencia: Bajista en el corto plazo, con soporte clave en zona de [valor].

2. Volumen: Por debajo del promedio, sugiriendo falta de convicción en los movimientos recientes.

3. Indicadores técnicos: MACD muestra señal de divergencia alcista, pero RSI sigue en territorio bajista.

4. Catalizadores: No hay eventos significativos programados que puedan afectar el precio en el corto plazo.

5. Recomendación: Precaución, esperar confirmación de reversión antes de tomar posiciones."""
            color = "warning"
        
        return analysis, color
