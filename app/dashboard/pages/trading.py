import dash
from dash import dcc, html, callback, Input, Output, State
from dash.dependencies import ClientsideFunction
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import os
import sys

# Agregar directorio raíz al path para importar módulos propios
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# Importar el cliente de datos de mercado y análisis técnico
from app.utils.market_data import MarketDataClient
from app.utils.technical_analysis import generate_analysis

# Crear una instancia global del cliente para toda la aplicación
market_data = MarketDataClient()

# Inicializar configuración desde un archivo si existe
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'config', 'exchanges.json')
config = {}
if os.path.exists(config_path):
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error al cargar configuración de exchanges: {e}")

# Inicializar cliente de datos de mercado
market_data = MarketDataClient(config)

def create_empty_chart():
    """Crear un gráfico vacío para mostrar inicialmente"""
    fig = go.Figure()
    
    fig.update_layout(
        title="Seleccione un par y haga clic en 'Cargar datos'",
        xaxis_title="Fecha/Hora",
        yaxis_title="Precio",
        template="plotly_dark",
        height=600,
        showlegend=True,
        # Mejorar la visualización de la escala de precios
        yaxis=dict(
            showgrid=True,
            zeroline=False,
            showticklabels=True,
            showline=True,
            title="Precio",
            tickprefix="$",  # Prefijo para precios
            tickformat=",.2f"  # Formato con dos decimales y comas para miles
        ),
        # Mejorar la configuración de interactividad
        modebar=dict(
            orientation='v',
            bgcolor='rgba(31,30,38,0.9)',
            color='white',
            activecolor='#1f77b4'
        )
    )
    
    return fig


def generate_complete_analysis(pair, timeframe, df=None):
    """Generar análisis técnico completo para el par y temporalidad dada"""
    
    # Obtener datos reales si no se proporcionan
    if df is None:
        try:
            # Usar el cliente global que ya hemos inicializado
            exchange = "binance"  # Por defecto
            df = market_data.get_market_data(
                exchange=exchange,
                symbol=pair,
                timeframe=timeframe,
                limit=100  # Suficientes datos para análisis
            )
        except Exception as e:
            # En caso de error, devolver un mensaje
            return f"""
            <div style="padding: 15px; margin-bottom: 20px; border-left: 4px solid #FF5555; background-color: rgba(255, 85, 85, 0.1);">
                <h3 style="color: #FF5555;">Error al obtener datos</h3>
                <p>No se pudieron obtener datos para realizar un análisis. {str(e)}</p>
            </div>
            """
    
    # Usar la función de análisis técnico del módulo especializado
    return generate_analysis(df, pair, timeframe)


# Definir el diseño de la página

# Layout principal de la página de trading - estilo Trading View
layout = html.Div([
    # Barra de navegación superior compacta con estilos mejorados
    dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    dbc.Row(
                        [
                            dbc.Col(html.Span('TradingRoad', className='ms-2 fw-bold', style={'color': '#4fc3f7', 'font-size': '1.5rem'})),
                        ],
                        align='center',
                        className='g-0',
                    ),
                    href='#',
                    style={'textDecoration': 'none'},
                ),
                dbc.NavbarToggler(id='navbar-toggler', n_clicks=0),
                dbc.Collapse(
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Button(
                                    [html.I(className='fas fa-sync me-1'), 'Cargar'],
                                    id='load-data-button',
                                    color='primary',
                                    size='sm',
                                ),
                                width='auto',
                                className='ms-0',
                            ),
                        ],
                        className='g-0 ms-auto flex-nowrap mt-3 mt-md-0',
                        align='center',
                    ),
                    id='navbar-collapse',
                    is_open=False,
                    navbar=True,
                ),
            ],
            fluid=True,
        ),
        dark=True,
        color='#131722',
        className='mb-2',
        style={'padding': '0.25rem 1rem', 'min-height': '48px'}
    ),
    
    # Controles para selección de exchange, par y timeframe
    html.Div(
        [
            dbc.Row(
                [
                    # Exchange selector - compacto
                    dbc.Col(
                        dcc.Dropdown(
                            id='exchange-selector',
                            options=[
                                {'label': 'Binance', 'value': 'binance'},
                                {'label': 'Bybit', 'value': 'bybit'},
                            ],
                            value='binance',
                            clearable=False,
                            style={'width': '100%', 'background': '#212121', 'color': 'white'}
                        ),
                        width={'size': 'auto', 'order': 1},
                        className='px-1'
                    ),
                    
                    # Par selector - compacto
                    dbc.Col(
                        dcc.Dropdown(
                            id='pair-selector',
                            options=[
                                {'label': 'BTC/USDT', 'value': 'BTC/USDT'},
                                {'label': 'ETH/USDT', 'value': 'ETH/USDT'},
                                {'label': 'XRP/USDT', 'value': 'XRP/USDT'},
                                {'label': 'SOL/USDT', 'value': 'SOL/USDT'},
                                {'label': 'DOGE/USDT', 'value': 'DOGE/USDT'},
                                {'label': 'ADA/USDT', 'value': 'ADA/USDT'},
                            ],
                            value='BTC/USDT',
                            clearable=False,
                            style={'width': '100%', 'background': '#212121', 'color': 'white'}
                        ),
                        width={'size': 2, 'order': 2},
                        className='px-1'
                    ),
                    
                    # Timeframe buttons - similar a TradingView
                    dbc.Col(
                        dbc.ButtonGroup(
                            [
                                dbc.Button('5m', id='tf-5m', color='dark', size='sm', outline=True, className='tf-button'),
                                dbc.Button('15m', id='tf-15m', color='dark', size='sm', outline=True, active=True, className='tf-button'),
                                dbc.Button('30m', id='tf-30m', color='dark', size='sm', outline=True, className='tf-button'),
                                dbc.Button('1h', id='tf-1h', color='dark', size='sm', outline=True, className='tf-button'),
                                dbc.Button('4h', id='tf-4h', color='dark', size='sm', outline=True, className='tf-button'),
                                dbc.Button('1d', id='tf-1d', color='dark', size='sm', outline=True, className='tf-button'),
                            ],
                            id='timeframe-buttons',
                            className='me-2'
                        ),
                        width={'size': 'auto', 'order': 3},
                        className='px-1'
                    ),
                    
                    # Indicadores como dropdown con checklist
                    dbc.Col(
                        dbc.DropdownMenu(
                            [
                                dbc.DropdownMenuItem('Medias Móviles', header=True),
                                dbc.DropdownMenuItem(
                                    dbc.Checklist(
                                        options=[
                                            {'label': 'SMA 20', 'value': 'sma_20'},
                                            {'label': 'SMA 50', 'value': 'sma_50'},
                                            {'label': 'SMA 200', 'value': 'sma_200'},
                                        ],
                                        value=[],
                                        id='sma-checklist',
                                        switch=True,
                                        inline=True,
                                    )
                                ),
                                dbc.DropdownMenuItem(divider=True),
                                dbc.DropdownMenuItem('Medias Exponenciales', header=True),
                                dbc.DropdownMenuItem(
                                    dbc.Checklist(
                                        options=[
                                            {'label': 'EMA 20', 'value': 'ema_20'},
                                            {'label': 'EMA 50', 'value': 'ema_50'},
                                            {'label': 'EMA 200', 'value': 'ema_200'},
                                        ],
                                        value=[],
                                        id='ema-checklist',
                                        switch=True,
                                        inline=True,
                                    )
                                ),
                                dbc.DropdownMenuItem(divider=True),
                                dbc.DropdownMenuItem('Otros Indicadores', header=True),
                                dbc.DropdownMenuItem(
                                    dbc.Checklist(
                                        options=[
                                            {'label': 'Bandas de Bollinger', 'value': 'bollinger'},
                                            {'label': 'RSI', 'value': 'rsi'},
                                            {'label': 'MACD', 'value': 'macd'},
                                        ],
                                        value=[],
                                        id='other-indicators-checklist',
                                        switch=True,
                                        inline=True,
                                    )
                                ),
                            ],
                            label='Indicadores',
                            color='dark',
                            className='m-0 p-0',
                            align_end=True,
                            style={'width': '100%'},
                        ),
                        width={'size': 2, 'order': 4},
                        className='px-1'
                    ),
                    
                    # Botón para actualización en tiempo real
                    dbc.Col(
                        dbc.Button(
                            [
                                html.I(className='fas fa-sync-alt me-1'),
                                'Tiempo Real',
                            ],
                            id='real-time-update',
                            color='success',
                            size='sm',
                            outline=True,
                            active=False,
                            n_clicks=0,
                        ),
                        width={'size': 'auto', 'order': 5},
                        className='px-1'
                    ),
                    
                    # Botón para cargar datos - consistente con el estilo
                    dbc.Col(
                        dbc.Button(
                            [
                                html.I(className='fas fa-chart-line me-1'),
                                'Cargar',
                            ],
                            id='load-data-button',
                            color='primary',
                            size='sm',
                            n_clicks=0,
                        ),
                        width={'size': 'auto', 'order': 6},
                        className='px-1'
                    ),
                ],
                className='g-0 align-items-center',
                style={'background': '#1e1e1e', 'padding': '5px'}
            ),
            # Componente de intervalo para actualización en tiempo real
            html.Div(
                dcc.Interval(
                    id='chart-interval',
                    interval=15000,  # 15 segundos entre actualizaciones
                    n_intervals=0,
                    disabled=True,  # Desactivado inicialmente
                ),
                style={'display': 'none'}
            )
        ],
        className='mb-1',
        style={'background': '#1e1e1e'}
    ),
    
    # Contenedor principal para el gráfico - ocupa casi toda la pantalla
    html.Div(
        [
            # Fila para el gráfico principal - estilo TradingView
            dbc.Row(
                [
                    # Columna única para el gráfico a pantalla completa
                    dbc.Col(
                        dcc.Graph(
                            id='trading-chart',
                            figure=create_empty_chart(),
                            style={'height': '80vh'},
                            config={
                                'displayModeBar': True,
                                'scrollZoom': True,
                                'displaylogo': False,
                                'modeBarButtonsToRemove': [
                                    'zoomIn', 'zoomOut', 'pan', 'select', 
                                    'lasso', 'autoScale'
                                ],
                                'toImageButtonOptions': {'format': 'png', 'filename': 'trading_chart'}
                            },
                        ),
                        width=12,
                        className='g-0'
                    ),
                ],
                className='g-0'
            ),
            
            # Panel flotante para análisis técnico
            html.Div(
                [
                    # Cabecera del panel
                    html.Div(
                        [
                            html.H5('Análisis Técnico Avanzado', className='mb-0 text-info'),
                            html.Button(
                                html.I(className='fas fa-times'),
                                id='close-analysis-panel',
                                className='btn-close btn-close-white',
                                style={'float': 'right'}
                            ),
                        ],
                        className='d-flex justify-content-between align-items-center mb-2'
                    ),
                    
                    # Contenido del análisis
                    html.Div(id='ai-analysis-content', style={'maxHeight': '400px', 'overflowY': 'auto'})
                ],
                id='analysis-panel',
                className='p-3',
                style={
                    'position': 'absolute',
                    'top': '70px',
                    'right': '20px',
                    'width': '400px',
                    'backgroundColor': 'rgba(25, 30, 47, 0.95)',
                    'border': '1px solid #2a2e39',
                    'borderRadius': '5px',
                    'zIndex': '1000',
                    'boxShadow': '0 4px 8px rgba(0,0,0,0.3)',
                    'display': 'none'
                }
            ),
        ],
        style={'position': 'relative'}
    ),
], className='p-0 m-0', style={'backgroundColor': '#131722', 'height': '100%'})


def register_callbacks(app):
    """Registrar los callbacks para la página de trading"""
    
    @app.callback(
        Output("analysis-panel", "style"),
        [Input("load-data-button", "n_clicks"), 
         Input("close-analysis-panel", "n_clicks")],
        [State("analysis-panel", "style")],
        prevent_initial_call=True
    )
    def toggle_analysis_panel(load_clicks, close_clicks, current_style):
        """Mostrar u ocultar el panel de análisis flotante"""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            return current_style
        
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if button_id == "load-data-button":
            # Mostrar panel cuando se cargan datos
            current_style["display"] = "block"
        elif button_id == "close-analysis-panel":
            # Ocultar panel cuando se cierra
            current_style["display"] = "none"
            
        return current_style
    
    # Interval para actualización en tiempo real 
    @app.callback(
        Output("chart-interval", "disabled"),
        Input("real-time-update", "active"),
        prevent_initial_call=True
    )
    def toggle_real_time_update(active):
        """Habilitar o deshabilitar el intervalo de actualización en tiempo real"""
        return not active  # Si el botón está activo, el intervalo NO está deshabilitado
        
    @app.callback(
        [Output("tf-5m", "active"),
         Output("tf-15m", "active"),
         Output("tf-30m", "active"),
         Output("tf-1h", "active"),
         Output("tf-4h", "active"),
         Output("tf-1d", "active")],
        [Input("tf-5m", "n_clicks"),
         Input("tf-15m", "n_clicks"),
         Input("tf-30m", "n_clicks"),
         Input("tf-1h", "n_clicks"),
         Input("tf-4h", "n_clicks"),
         Input("tf-1d", "n_clicks")],
        prevent_initial_call=True
    )
    def update_active_timeframe(click_5m, click_15m, click_30m, click_1h, click_4h, click_1d):
        """Actualiza qué botón de timeframe está activo"""
        ctx = dash.callback_context
        if not ctx.triggered:
            # Por defecto, 15m activo
            return False, True, False, False, False, False
        
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Solo el botón clickeado estará activo
        states = [False] * 6
        if button_id == "tf-5m":
            states[0] = True
        elif button_id == "tf-15m":
            states[1] = True
        elif button_id == "tf-30m":
            states[2] = True
        elif button_id == "tf-1h":
            states[3] = True
        elif button_id == "tf-4h":
            states[4] = True
        elif button_id == "tf-1d":
            states[5] = True
        
        return states
    
    @app.callback(
        [
            Output("trading-chart", "figure"),
            Output("ai-analysis-content", "children")
        ],
        [Input("load-data-button", "n_clicks"),
         # Intervalo para actualización en tiempo real
         Input("chart-interval", "n_intervals"),
         # Botones de timeframe como triggers
         Input("tf-5m", "n_clicks"),
         Input("tf-15m", "n_clicks"),
         Input("tf-30m", "n_clicks"),
         Input("tf-1h", "n_clicks"),
         Input("tf-4h", "n_clicks"),
         Input("tf-1d", "n_clicks")],
        [State("exchange-selector", "value"),
         State("pair-selector", "value"),
         # Ya no necesitamos timeframe-selector, usando botones
         # State("timeframe-selector", "value"),
         # Nuevos checkboxes para indicadores
         State("sma-checklist", "value"),
         State("ema-checklist", "value"),
         State("other-indicators-checklist", "value"),
         # Estado del botón de tiempo real
         State("real-time-update", "active")],
        prevent_initial_call=True
    )
    def update_trading_chart(load_clicks, n_intervals, tf_5m_clicks, tf_15m_clicks, tf_30m_clicks, tf_1h_clicks, 
                           tf_4h_clicks, tf_1d_clicks, exchange, pair, sma_indicators, ema_indicators, 
                           other_indicators, real_time_update):
        """Actualiza el gráfico de trading con los datos seleccionados en tiempo real y genera análisis detallado"""
        
        # Determinar qué botón de timeframe fue clickeado
        ctx = dash.callback_context
        button_id = ""
        if ctx.triggered:
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            
        # Determinar el timeframe seleccionado
        timeframe = "15m"  # Por defecto
        if button_id == "tf-5m":
            timeframe = "5m"
        elif button_id == "tf-15m":
            timeframe = "15m"
        elif button_id == "tf-30m":
            timeframe = "30m"
        elif button_id == "tf-1h":
            timeframe = "1h"
        elif button_id == "tf-4h":
            timeframe = "4h"
        elif button_id == "tf-1d":
            timeframe = "1d"
        
        # Mapear periodos de timeframe a número de velas
        periods_map = {
            "5m": 150,
            "15m": 150,
            "30m": 120,
            "1h": 100,
            "4h": 100,
            "1d": 100
        }
        
        limit = periods_map.get(timeframe, 100)
        
        # Obtener datos reales del mercado usando nuestro cliente
        df = market_data.get_market_data(
            exchange=exchange,
            symbol=pair,
            timeframe=timeframe,
            limit=limit
        )
        
        # Si no hay datos o hubo un error, mostrar mensaje
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text=f"No se pudieron obtener datos de {exchange} para {pair}",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                font=dict(size=16, color="white")
            )
            fig.update_layout(
                template="plotly_dark",
                height=600
            )
            
            # Enviar mensaje de error para el análisis
            error_analysis = f"<div style='color: white;'>No se pudieron cargar datos de {exchange} para el par {pair}.</div>"
            return fig, html.Div([
                html.Div(dangerouslySetInnerHTML={'__html': error_analysis})
            ], style={'max-height': '600px', 'overflow-y': 'auto', 'padding': '10px', 'color': 'white'})
        
        # Extraer datos para el gráfico
        dates = df['timestamp']
        open_values = df['open']
        high_values = df['high']
        low_values = df['low']
        close_values = df['close']
        volume_values = df['volume']
        
        # Determinar los valores min/max para la escala de precios adecuada
        min_price = low_values.min() * 0.999  # Ligero margen para visualización
        max_price = high_values.max() * 1.001  # Ligero margen para visualización
        price_range = max_price - min_price
        tick_spacing = price_range / 10  # 10 divisiones en el eje Y
        
        # Crear figura con Plotly con estilo mejorado - usamos subplots para agregar volumen
        fig = make_subplots(
            rows=2, cols=1, 
            shared_xaxes=True, 
            vertical_spacing=0.03, 
            row_heights=[0.8, 0.2],
            subplot_titles=(f"{pair} - {timeframe} - {exchange.capitalize()}", "Volumen")
        )
        
        # Añadir gráfico de velas al subplot principal
        fig.add_trace(
            go.Candlestick(
                x=dates,
                open=open_values, 
                high=high_values,
                low=low_values, 
                close=close_values,
                name=pair,
                increasing_line_color='#26A69A',  # Color para velas alcistas
                decreasing_line_color='#EF5350'   # Color para velas bajistas
            ),
            row=1, col=1
        )
        
        # Añadir volumen abajo
        colors = ['#26A69A' if close_values[i] >= open_values[i] else '#EF5350' for i in range(len(close_values))]
        fig.add_trace(
            go.Bar(
                x=dates,
                y=volume_values,
                name="Volumen",
                marker_color=colors,
                opacity=0.8
            ),
            row=2, col=1
        )
        
        # Agregar líneas horizontales para máximos y mínimos
        fig.add_shape(
            type="line",
            x0=dates.iloc[0],
            y0=high_values.max(),
            x1=dates.iloc[-1],
            y1=high_values.max(),
            line=dict(color="rgba(255,255,255,0.5)", width=1, dash="dot"),
            row=1, col=1
        )
        
        fig.add_shape(
            type="line",
            x0=dates.iloc[0],
            y0=low_values.min(),
            x1=dates.iloc[-1],
            y1=low_values.min(),
            line=dict(color="rgba(255,255,255,0.5)", width=1, dash="dot"),
            row=1, col=1
        )
        
        # Añadir anotaciones para máximos y mínimos
        fig.add_annotation(
            x=dates.iloc[-1],
            y=high_values.max(),
            text=f"Máx: {high_values.max():.2f}",
            showarrow=False,
            font=dict(size=10, color="white"),
            xanchor="right",
            yanchor="bottom",
            bgcolor="rgba(30,30,30,0.7)",
            bordercolor="white",
            borderpad=2,
            row=1, col=1
        )
        
        fig.add_annotation(
            x=dates.iloc[-1],
            y=low_values.min(),
            text=f"Mín: {low_values.min():.2f}",
            showarrow=False,
            font=dict(size=10, color="white"),
            xanchor="right",
            yanchor="top",
            bgcolor="rgba(30,30,30,0.7)",
            bordercolor="white",
            borderpad=2,
            row=1, col=1
        )
        
        # Define colores para los indicadores
        sma_colors = ['#FF9800', '#2196F3', '#4CAF50']  # Naranja, Azul, Verde
        ema_colors = ['#E91E63', '#9C27B0', '#673AB7']   # Rosa, Morado, Índigo
        
        # Añadir SMAs seleccionadas
        if sma_indicators:
            # Diccionario de ventanas para SMA
            sma_windows = {
                'sma_20': 20,
                'sma_50': 50,
                'sma_200': 200
            }
            
            for i, sma_id in enumerate(sma_indicators):
                window = sma_windows.get(sma_id, 20)  # Por defecto usa 20 si no encuentra
                color_index = min(i, len(sma_colors)-1)  # Evitar índice fuera de rango
                
                sma = pd.Series(close_values).rolling(window=window).mean()
                fig.add_trace(
                    go.Scatter(
                        x=dates,
                        y=sma,
                        name=f"SMA({window})",
                        line=dict(color=sma_colors[color_index], width=1.5)
                    ),
                    row=1, col=1
                )
        
        # Añadir EMAs seleccionadas
        if ema_indicators:
            # Diccionario de ventanas para EMA
            ema_windows = {
                'ema_9': 9,
                'ema_21': 21,
                'ema_55': 55
            }
            
            for i, ema_id in enumerate(ema_indicators):
                window = ema_windows.get(ema_id, 21)  # Por defecto usa 21 si no encuentra
                color_index = min(i, len(ema_colors)-1)  # Evitar índice fuera de rango
                
                ema = pd.Series(close_values).ewm(span=window, adjust=False).mean()
                fig.add_trace(
                    go.Scatter(
                        x=dates,
                        y=ema,
                        name=f"EMA({window})",
                        line=dict(color=ema_colors[color_index], width=1.5)
                    ),
                    row=1, col=1
                )
        
        # Añadir otros indicadores
        if other_indicators:
            # Bandas de Bollinger
            if "bollinger" in other_indicators:
                sma_20 = pd.Series(close_values).rolling(window=20).mean()
                std_20 = pd.Series(close_values).rolling(window=20).std()
                upper_band = sma_20 + 2 * std_20
                lower_band = sma_20 - 2 * std_20
                
                fig.add_trace(
                    go.Scatter(
                        x=dates,
                        y=upper_band,
                        name="BB Upper",
                        line=dict(color='rgba(236, 64, 122, 0.7)', width=1.0),
                        legendgroup="bollinger"
                    ),
                    row=1, col=1
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=dates,
                        y=lower_band,
                        name="BB Lower",
                        fill='tonexty',
                        fillcolor='rgba(236, 64, 122, 0.05)',
                        line=dict(color='rgba(236, 64, 122, 0.7)', width=1.0),
                        legendgroup="bollinger"
                    ),
                    row=1, col=1
                )
            
            # RSI
            if "rsi" in other_indicators:
                # Calculamos RSI
                delta = pd.Series(close_values).diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                
                # Creamos un subplot adicional para RSI
                fig.add_trace(
                    go.Scatter(
                        x=dates,
                        y=rsi,
                        name="RSI(14)",
                        line=dict(color='#64B5F6', width=1.5)
                    ),
                    row=2, col=1
                )
                
                # Añadimos líneas de niveles
                fig.add_shape(
                    type="line", line=dict(dash='dash', color='#FF9800'),
                    x0=dates.iloc[0], x1=dates.iloc[-1], y0=70, y1=70,
                    row=2, col=1
                )
                fig.add_shape(
                    type="line", line=dict(dash='dash', color='#FF9800'),
                    x0=dates.iloc[0], x1=dates.iloc[-1], y0=30, y1=30,
                    row=2, col=1
                )
                fig.add_shape(
                    type="line", line=dict(dash='dot', color='#B0BEC5'),
                    x0=dates.iloc[0], x1=dates.iloc[-1], y0=50, y1=50,
                    row=2, col=1
                )
                
                # Añadimos etiquetas de niveles
                fig.add_annotation(
                    x=dates.iloc[-1], y=70,
                    text="70",
                    showarrow=False,
                    font=dict(size=10, color="#FF9800"),
                    xanchor="right",
                    yanchor="bottom",
                    row=2, col=1
                )
                fig.add_annotation(
                    x=dates.iloc[-1], y=30,
                    text="30",
                    showarrow=False,
                    font=dict(size=10, color="#FF9800"),
                    xanchor="right",
                    yanchor="top",
                    row=2, col=1
                )
            
            # MACD
            if "macd" in other_indicators:
                # Calculamos MACD
                ema_12 = pd.Series(close_values).ewm(span=12, adjust=False).mean()
                ema_26 = pd.Series(close_values).ewm(span=26, adjust=False).mean()
                macd_line = ema_12 - ema_26
                signal_line = macd_line.ewm(span=9, adjust=False).mean()
                histogram = macd_line - signal_line
                
                # Si ya tenemos RSI, creamos una tercera fila para MACD
                macd_row = 3 if "rsi" in other_indicators else 2
                
                # Si necesitamos una tercera fila para MACD, la creamos
                if macd_row == 3:
                    fig = make_subplots(
                        rows=3, cols=1, 
                        shared_xaxes=True, 
                        vertical_spacing=0.05, 
                        row_heights=[0.6, 0.2, 0.2],
                        subplot_titles=(f"{pair} - {timeframe} - {exchange.capitalize()}", "RSI", "MACD")
                    )
                    
                    # Volver a añadir la vela principal
                    fig.add_trace(
                        go.Candlestick(
                            x=dates,
                            open=open_values, 
                            high=high_values,
                            low=low_values, 
                            close=close_values,
                            name=pair,
                            increasing_line_color='#26A69A',  # Color para velas alcistas
                            decreasing_line_color='#EF5350'   # Color para velas bajistas
                        ),
                        row=1, col=1
                    )
                    
                    # Volver a añadir el volumen
                    colors = ['#26A69A' if close_values[i] >= open_values[i] else '#EF5350' for i in range(len(close_values))]
                    fig.add_trace(
                        go.Bar(
                            x=dates,
                            y=volume_values,
                            name="Volumen",
                            marker_color=colors,
                            opacity=0.8
                        ),
                        row=2, col=1
                    )
            
            # Añadir MACD si está seleccionado
            if other_indicators and "macd" in other_indicators:
                print("Añadiendo MACD al gráfico")
                # Calcular MACD
                macd_line = df['macd_line'].values
                signal_line = df['signal_line'].values
                histogram = df['macd_hist'].values
                
                # Añadir el histograma MACD
                fig.add_trace(
                    go.Bar(
                        x=dates,
                        y=histogram,
                        name="MACD Hist",
                        marker_color=['#26A69A' if val >= 0 else '#EF5350' for val in histogram],
                        opacity=0.7
                    ),
                    row=macd_row, col=1
                )
                
                # Añadir líneas MACD
                fig.add_trace(
                    go.Scatter(
                        x=dates,
                        y=macd_line,
                        name="MACD",
                        line=dict(color='#2196F3', width=1.5)
                    ),
                    row=macd_row, col=1
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=dates,
                        y=signal_line,
                        name="Signal",
                        line=dict(color='#FF9800', width=1.5)
                    ),
                    row=macd_row, col=1
                )
        
        # Añadir Bandas de Bollinger si están seleccionadas
        if other_indicators and "bollinger" in other_indicators:
            upper_band = df['upper_band'].values
            middle_band = df['middle_band'].values
            lower_band = df['lower_band'].values
            
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=upper_band,
                    name="BB Upper",
                    line=dict(color='rgba(236, 64, 122, 0.7)', width=1.0),
                    legendgroup="bollinger"
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=middle_band,
                    name="BB Middle",
                    line=dict(color='rgba(255, 235, 59, 0.7)', width=1.0),
                    legendgroup="bollinger"
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=lower_band,
                    name="BB Lower",
                    line=dict(color='rgba(236, 64, 122, 0.7)', width=1.0),
                    legendgroup="bollinger"
                ),
                row=1, col=1
            )
        
        # Actualizar layout con mejor escala y visibilidad (estilo TradingView)
        fig.update_layout(
            height=700,  # Altura adecuada para pantalla completa
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0.05,
                font=dict(size=10)
            ),
            margin=dict(l=40, r=40, b=40, t=60, pad=10),
            hovermode="closest",
            plot_bgcolor="#131722",  # Color de fondo similar a TradingView
            paper_bgcolor="#131722",
            dragmode="zoom",  # Permite arrastrar para hacer zoom
            modebar=dict(
                orientation='v',
                bgcolor='rgba(0,0,0,0)',
                color='white',
                activecolor='#2196F3'
            ),
            transition_duration=300  # Animación suave al actualizar
        )
        
        # Configurar eje Y para la escala de precios más precisa
        fig.update_yaxes(
            row=1, col=1,
            showgrid=True,
            gridwidth=0.5,
            gridcolor='rgba(120, 125, 136, 0.2)',  # Color de cuadrícula más claro y sutil
            zeroline=False,
            showticklabels=True,
            showline=True,
            linewidth=1,
            linecolor='rgba(180, 180, 180, 0.3)',
            title="",  # Sin título para más espacio
            tickprefix="$",  # Prefijo para precios
            tickformat=",.2f",  # Formato con dos decimales y comas para miles
            # Fijar el rango para mostrar máximos y mínimos con un margen
            range=[min_price * 0.998, max_price * 1.002],
            # Añadir ticks intermedios para mejor visualización
            dtick=tick_spacing,
            tickfont=dict(size=10)
        )
        
        # Configurar eje X para fechas
        fig.update_xaxes(
            rangeslider=dict(visible=False),  # Desactivar rangeslider para más espacio
            showgrid=True,
            gridwidth=0.5,
            gridcolor='rgba(120, 125, 136, 0.2)',
            showline=True,
            linewidth=1,
            linecolor='rgba(180, 180, 180, 0.3)',
            tickfont=dict(size=10),
            title="",  # Sin título para el eje X (fecha/hora)
            row=1, col=1
        )
        
        # Configurar eje Y para volumen
        fig.update_yaxes(
            row=2, col=1,
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            title="Vol",
            tickfont=dict(size=8, color="white")
        )
        
        # Configurar eje X para volumen
        fig.update_xaxes(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            title="Fecha/Hora",
            tickfont=dict(size=10, color="white"),
            row=2, col=1
        )
        
        # Añadir información sobre actualización en tiempo real si está activa
        if real_time_update:
            fig.add_annotation(
                xref="paper", yref="paper",
                x=1, y=0,
                text="Actualización en Tiempo Real",
                showarrow=False,
                font=dict(color="#4CAF50", size=10),
                bgcolor="rgba(0,0,0,0.5)",
                borderpad=4,
                align="right",
                xanchor="right",
                yanchor="bottom"
            )
        
        # Generar análisis detallado usando la función que creamos
        analysis = generate_complete_analysis(pair, timeframe)
        
        # Devolver tanto el gráfico como el análisis detallado
        return fig, html.Div([
            html.Div([
                html.H5(f"Análisis Técnico: {pair} - {timeframe}", className="mb-3"),
                html.Div(dangerouslySetInnerHTML={
                    '__html': analysis
                })
            ])
        ], style={'max-height': '600px', 'overflow-y': 'auto', 'padding': '15px', 'color': 'white', 'background-color': '#1e222d', 'border': '1px solid #2a2e39', 'border-radius': '5px'})
    
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
