import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# Layout principal de la página de inicio
layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.H2("Bienvenido a TradingRoad", className="text-primary"),
            html.P("Plataforma avanzada de trading con análisis en tiempo real y conexiones a múltiples exchanges"),
            html.Hr(),
        ], width=12)
    ]),
    
    dbc.Row([
        # Panel de resumen
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Resumen de mercado", className="card-title")),
                dbc.CardBody([
                    html.Div(id='market-summary-content', children=[
                        html.P("Cargando datos de mercado...", id="loading-text"),
                        dbc.Spinner(html.Div(id="market-data-container"))
                    ])
                ])
            ]),
        ], width=12, lg=6, className="mb-4"),
        
        # Panel de noticias
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Noticias y eventos", className="card-title")),
                dbc.CardBody([
                    html.Div(id='news-content', children=[
                        # Se llenará con el callback
                        html.P("Últimas noticias del mercado de criptomonedas")
                    ])
                ])
            ]),
        ], width=12, lg=6, className="mb-4"),
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Gráfico de ejemplo", className="card-title")),
                dbc.CardBody([
                    dcc.Graph(
                        id='example-chart',
                        figure=create_example_chart()
                    )
                ])
            ]),
        ], width=12, className="mb-4"),
    ]),
])

def create_example_chart():
    """Crear un gráfico de ejemplo para mostrar en la página de inicio"""
    # Crear datos de ejemplo para un gráfico de velas
    dates = pd.date_range(start='2023-01-01', periods=30, freq='D')
    
    # Generar precios simulados
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(30) * 2)
    open = close - np.random.randn(30) * 1.5
    high = np.maximum(close, open) + np.random.rand(30) * 3
    low = np.minimum(close, open) - np.random.rand(30) * 3
    
    # Crear figura con Plotly
    fig = go.Figure(data=[go.Candlestick(
        x=dates,
        open=open, 
        high=high,
        low=low, 
        close=close,
        name='BTC/USD'
    )])
    
    # Actualizar layout
    fig.update_layout(
        title='Bitcoin/USD - Últimos 30 días (Datos de ejemplo)',
        xaxis_title='Fecha',
        yaxis_title='Precio (USD)',
        template='plotly_dark',
        height=500,
        margin=dict(l=50, r=50, t=70, b=50),
    )
    
    return fig

def register_callbacks(app):
    """Registrar los callbacks para la página de inicio"""
    
    @app.callback(
        Output('market-data-container', 'children'),
        Output('loading-text', 'style'),
        Input('session-store', 'data')
    )
    def update_market_summary(session_data):
        """Actualiza el resumen de mercado"""
        # Simulamos algunos datos de mercado
        market_data = [
            {"symbol": "BTC/USD", "price": "43,562.45", "change": "+2.3%", "color": "success"},
            {"symbol": "ETH/USD", "price": "2,345.67", "change": "+1.5%", "color": "success"},
            {"symbol": "BNB/USD", "price": "345.23", "change": "-0.7%", "color": "danger"},
            {"symbol": "XRP/USD", "price": "0.5678", "change": "+0.2%", "color": "success"},
            {"symbol": "ADA/USD", "price": "0.4523", "change": "-1.2%", "color": "danger"}
        ]
        
        # Crear un componente para mostrar los datos
        market_summary = html.Div([
            html.Table([
                html.Thead(
                    html.Tr([
                        html.Th("Símbolo"),
                        html.Th("Precio"),
                        html.Th("Cambio 24h")
                    ])
                ),
                html.Tbody([
                    html.Tr([
                        html.Td(item["symbol"]),
                        html.Td(item["price"]),
                        html.Td(item["change"], className=f"text-{item['color']}")
                    ]) for item in market_data
                ])
            ], className="table table-striped table-hover")
        ])
        
        # Ocultar el texto de carga
        loading_style = {'display': 'none'}
        
        return market_summary, loading_style
