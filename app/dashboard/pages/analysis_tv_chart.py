"""Componente simplificado de gráfico TradingView compatible con Render"""
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import json
import os

def create_tv_chart_component(height=700):
    """
    Crea el componente de gráfico de TradingView Lightweight Charts simplificado
    
    Args:
        height: Altura del gráfico en píxeles
        
    Returns:
        Componente HTML con el gráfico de TradingView
    """
    return html.Div([
        # Cabecera con controles
        html.Div([
            dbc.Row([
                # Columna izquierda: Dropdown de fuente de datos
                dbc.Col([
                    html.Div([
                        html.Label("Data Source", className="text-light mb-1 small"),
                        dcc.Dropdown(
                            id="tv-exchange-dropdown",
                            options=[
                                {"label": "Binance Futures", "value": "binance_futures"},
                                {"label": "Binance Spot", "value": "binance"},
                            ],
                            value="binance_futures",
                            className="tv-dropdown dark-dropdown",
                        ),
                    ]),
                ], width=3),
                
                # Columna central: Par de trading
                dbc.Col([
                    html.Div([
                        html.Label("Trading Pair / Symbol", className="text-light mb-1 small"),
                        dbc.Input(
                            id="tv-symbol-input",
                            value="ETHUSDT",
                            type="text",
                            className="tv-input",
                        ),
                    ]),
                ], width=3),
                
                # Columna derecha: Botones de timeframe
                dbc.Col([
                    html.Div([
                        html.Label("Timeframe", className="text-light mb-1 small"),
                        dbc.ButtonGroup(
                            [
                                dbc.Button("1H", id="tv-tf-1h", color="primary", size="sm"),
                                dbc.Button("4H", id="tv-tf-4h", color="dark", size="sm", outline=True),
                                dbc.Button("1D", id="tv-tf-1d", color="dark", size="sm", outline=True),
                            ],
                        ),
                    ]),
                ], width=6),
            ], className="mb-2"),
        ], className="tv-controls px-3 py-2"),

        # Contenedor principal para el gráfico
        dbc.Row([
            # Gráfico principal
            dbc.Col([
                html.Div(
                    id="tradingview-chart-container",
                    style={"width": "100%", "height": f"{height}px", "position": "relative"}
                ),
            ], width=12),
        ]),
        
        # Almacenamiento de datos
        dcc.Store(id="tv-chart-data", data=None),
        dcc.Store(id="tv-timeframe", data="1h"),
        
        # Script para Lightweight Charts desde CDN
        html.Div([
            html.Script(
                src="https://unpkg.com/lightweight-charts@4.1.0/dist/lightweight-charts.standalone.production.js"
            )
        ])
    ])


def prepare_tv_chart_data(df):
    """
    Prepara los datos del DataFrame para TradingView Lightweight Charts
    
    Args:
        df: DataFrame con datos OHLCV
        
    Returns:
        Dict con datos formateados para el gráfico
    """
    # Verificar si el DataFrame está vacío o es None
    if df is None or df.empty:
        return None
    
    # Crear datos para velas
    candles = []
    volumes = []
    
    for idx, row in df.iterrows():
        # Asegurarnos que tenemos un timestamp en milisegundos
        if isinstance(idx, pd.Timestamp):
            time_ms = int(idx.timestamp() * 1000)
        elif isinstance(idx, (int, float)):
            # Si ya es un timestamp numérico (epoch)
            time_ms = int(idx * 1000) if idx < 10**12 else int(idx)  # Convertir a ms si es necesario
        else:
            # Intentar convertir a timestamp si es string
            try:
                time_ms = int(pd.Timestamp(idx).timestamp() * 1000)
            except:
                continue  # Saltar filas con timestamps inválidos
        
        # Datos de vela
        candle = {
            'time': time_ms,
            'open': float(row['open']),
            'high': float(row['high']),
            'low': float(row['low']),
            'close': float(row['close'])
        }
        candles.append(candle)
        
        # Datos de volumen
        if 'volume' in row:
            volume = {
                'time': time_ms,
                'value': float(row['volume']),
                'color': '#26a69a' if row['close'] >= row['open'] else '#ef5350'
            }
            volumes.append(volume)
    
    return {
        'candles': candles,
        'volumes': volumes
    }


def register_tv_chart_callbacks(app):
    """
    Registra los callbacks necesarios para el funcionamiento del gráfico TradingView
    
    Args:
        app: Aplicación Dash
    """
    @app.callback(
        Output('tv-chart-data', 'data'),
        [Input('analysis-load-data-signal', 'data'), 
         Input('real-time-update-interval', 'n_intervals')],
        [State('analysis-chart-data', 'data'), 
         State('real-time-update-toggle', 'value')]
    )
    def update_tv_chart_data(load_signal, n_intervals, chart_data, real_time_enabled):
        if chart_data is None:
            return None
            
        # Convertir los datos a un formato para TradingView
        try:
            df = pd.DataFrame(chart_data)
            df.set_index('timestamp', inplace=True)
            return prepare_tv_chart_data(df)
        except Exception as e:
            print(f"Error al preparar datos para TradingView: {e}")
            return None

    # Callback clientside para inicializar y actualizar el gráfico
    app.clientside_callback(
        """
        function(chartData, timeframe) {
            // Si no hay datos, no hacer nada
            if (!chartData) return window.dash_clientside.no_update;
            
            // Si el elemento del gráfico no existe, no hacer nada
            const chartElement = document.getElementById('tradingview-chart-container');
            if (!chartElement) return window.dash_clientside.no_update;
            
            // Si el objeto window.chart ya existe, actualizar sus datos
            if (window.chart && window.candleSeries) {
                window.candleSeries.setData(chartData.candles);
                if (window.volumeSeries && chartData.volumes) {
                    window.volumeSeries.setData(chartData.volumes);
                }
                return window.dash_clientside.no_update;
            }
            
            // Crear una nueva instancia del gráfico
            const chartOptions = {
                width: chartElement.clientWidth,
                height: chartElement.clientHeight,
                layout: { 
                    background: { color: '#131722' },
                    textColor: '#d1d4dc',
                },
                grid: {
                    vertLines: { color: 'rgba(42, 46, 57, 0.6)' },
                    horzLines: { color: 'rgba(42, 46, 57, 0.6)' },
                },
                timeScale: {
                    timeVisible: true,
                },
                watermark: {
                    visible: true,
                    fontSize: 40,
                    color: 'rgba(224, 227, 235, 0.05)',
                    text: 'TradingRoad',
                }
            };
            
            // Crear el gráfico
            window.chart = LightweightCharts.createChart(chartElement, chartOptions);
            
            // Crear la serie de velas
            window.candleSeries = window.chart.addCandlestickSeries({
                upColor: '#26a69a',
                downColor: '#ef5350',
                borderUpColor: '#26a69a',
                borderDownColor: '#ef5350',
                wickUpColor: '#26a69a',
                wickDownColor: '#ef5350',
            });
            
            // Agregar los datos de velas
            if (chartData.candles) {
                window.candleSeries.setData(chartData.candles);
            }
            
            // Agregar serie de volumen
            window.volumeSeries = window.chart.addHistogramSeries({
                priceFormat: { type: 'volume' },
                priceScaleId: 'volume',
                scaleMargins: { top: 0.8, bottom: 0 },
            });
            
            // Agregar datos de volumen
            if (chartData.volumes) {
                window.volumeSeries.setData(chartData.volumes);
            }
            
            // Ajustar cuando cambie el tamaño
            const resizeObserver = new ResizeObserver(() => {
                window.chart.applyOptions({ 
                    width: chartElement.clientWidth,
                    height: chartElement.clientHeight
                });
            });
            resizeObserver.observe(chartElement);
            
            return window.dash_clientside.no_update;
        }
        """,
        Output('tradingview-chart-container', 'children'),
        [Input('tv-chart-data', 'data'), Input('tv-timeframe', 'data')]
    )
    
    # Callback para cambiar el timeframe
    @app.callback(
        Output('tv-timeframe', 'data'),
        [
            Input('tv-tf-1h', 'n_clicks'),
            Input('tv-tf-4h', 'n_clicks'),
            Input('tv-tf-1d', 'n_clicks'),
        ],
        [State('tv-timeframe', 'data')]
    )
    def update_timeframe(btn_1h, btn_4h, btn_1d, current_tf):
        ctx = dash.callback_context
        if not ctx.triggered:
            return current_tf
        
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if button_id == 'tv-tf-1h':
            return "1h"
        elif button_id == 'tv-tf-4h':
            return "4h"
        elif button_id == 'tv-tf-1d':
            return "1d"
        
        return current_tf
