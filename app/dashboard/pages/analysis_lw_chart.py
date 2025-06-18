import dash
from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
import os

from app.utils.market_data import get_ohlcv_data
from app.utils.technical_analysis import get_technical_indicators

# Página de análisis técnico avanzado con TradingView charts
def create_analysis_lw_page():
    """
    Crea la página de análisis técnico utilizando lightweight-charts
    """
    layout = html.Div([
        # Almacenamiento de datos
        dcc.Store(id='analysis-lw-chart-data', data={}),
        dcc.Store(id='analysis-lw-load-data-signal', data={'timestamp': time.time()}),
        dcc.Store(id='lw-timeframe', data='1h'),
        
        # Intervalo de actualización en tiempo real específico para lightweight charts
        dcc.Interval(
            id='lw-real-time-update-interval',
            interval=15000,  # en milisegundos (15 seg)
            n_intervals=0,
            disabled=True
        ),
        
        # Controles de datos
        html.Div([
            dbc.Row([
                # Exchange selector
                dbc.Col([
                    html.Label("Exchange:", className="control-label"),
                    dcc.Dropdown(
                        id='analysis-exchange-selector',
                        options=[
                            {'label': 'Binance', 'value': 'binance'},
                            {'label': 'Coinbase', 'value': 'coinbase'},
                            {'label': 'KuCoin', 'value': 'kucoin'},
                            {'label': 'Bitfinex', 'value': 'bitfinex'},
                        ],
                        value='binance',
                        clearable=False,
                        className="dash-dropdown"
                    ),
                ], width=2),
                
                # Symbol selector
                dbc.Col([
                    html.Label("Par:", className="control-label"),
                    dcc.Dropdown(
                        id='analysis-symbol-selector',
                        options=[
                            {'label': 'BTC/USDT', 'value': 'BTC/USDT'},
                            {'label': 'ETH/USDT', 'value': 'ETH/USDT'},
                            {'label': 'SOL/USDT', 'value': 'SOL/USDT'},
                            {'label': 'XRP/USDT', 'value': 'XRP/USDT'},
                            {'label': 'BNB/USDT', 'value': 'BNB/USDT'},
                        ],
                        value='ETH/USDT',
                        clearable=False,
                        className="dash-dropdown"
                    ),
                ], width=2),
                
                # Timeframe selector
                dbc.Col([
                    html.Label("Timeframe:", className="control-label"),
                    dcc.Dropdown(
                        id='analysis-timeframe-selector',
                        options=[
                            {'label': '1 minuto', 'value': '1m'},
                            {'label': '5 minutos', 'value': '5m'},
                            {'label': '15 minutos', 'value': '15m'},
                            {'label': '30 minutos', 'value': '30m'},
                            {'label': '1 hora', 'value': '1h'},
                            {'label': '4 horas', 'value': '4h'},
                            {'label': '1 día', 'value': '1d'},
                        ],
                        value='5m',
                        clearable=False,
                        className="dash-dropdown"
                    ),
                ], width=2),
                
                # Real-time toggle
                dbc.Col([
                    html.Label("Actualización:", className="control-label"),
                    dbc.Switch(
                        id='real-time-update-toggle',
                        label="Tiempo real",
                        value=False,
                        className="toggle-switch"
                    ),
                ], width=3, className="d-flex align-items-center"),
            ]),
        ], className="controls-container mb-3"),
        
        # Contenedor principal para el gráfico
        html.Div([
            html.Div(id='lightweight-chart-container', className='chart-container'),
        ], className="main-chart-container"),
        
        # JavaScript y CSS necesario para lightweight-charts
        html.Div([
            # CSS
            html.Style('''
                .chart-container {
                    width: 100%;
                    height: 600px;
                    position: relative;
                    background-color: #131722;
                    border-radius: 8px;
                    overflow: hidden;
                }
                .controls-container {
                    padding: 15px;
                    background-color: #1E222D;
                    border-radius: 8px;
                    margin-bottom: 15px;
                }
                .control-label {
                    color: #D1D4DC;
                    margin-bottom: 5px;
                    font-size: 0.9rem;
                }
                .dash-dropdown .Select-control {
                    background-color: #2A2E39;
                    border-color: #363A45;
                    color: #D1D4DC;
                }
                .dash-dropdown .Select-menu-outer {
                    background-color: #2A2E39;
                    border-color: #363A45;
                    color: #D1D4DC;
                }
                .dash-dropdown .Select-value-label {
                    color: #D1D4DC !important;
                }
                .toggle-switch {
                    margin-top: 25px;
                }
            '''),
            
            # JavaScript clientside para lightweight-charts
            dcc.ClientsideFunction(
                namespace='clientside',
                function_name='renderLightweightChart',
                id='clientside-lightweight-chart'
            ),
            
            # Código JavaScript para inicializar y actualizar el gráfico
            html.Script('''
                if (!window.dash_clientside) {
                    window.dash_clientside = {};
                }
                
                window.dash_clientside.clientside = {
                    renderLightweightChart: function(chartData, timeframe) {
                        const container = document.getElementById('lightweight-chart-container');
                        if (!container) return null;
                        
                        // Limpiar el contenedor si ya hay un gráfico
                        container.innerHTML = '';
                        
                        // Si no hay datos, no hacer nada
                        if (!chartData || !chartData.candles || chartData.candles.length === 0) {
                            return null;
                        }
                        
                        // Crear el gráfico
                        const chart = LightweightCharts.createChart(container, {
                            layout: {
                                background: { color: '#131722' },
                                textColor: '#D1D4DC',
                            },
                            grid: {
                                vertLines: { color: '#242732' },
                                horzLines: { color: '#242732' },
                            },
                            timeScale: {
                                timeVisible: true,
                                secondsVisible: timeframe.includes('m'),
                                borderColor: '#363A45',
                            },
                            width: container.clientWidth,
                            height: container.clientHeight,
                            rightPriceScale: {
                                borderColor: '#363A45',
                            },
                        });
                        
                        // Ajustar tamaño al cambiar la ventana
                        window.addEventListener('resize', () => {
                            chart.resize(container.clientWidth, container.clientHeight);
                        });
                        
                        // Añadir serie de velas
                        const candleSeries = chart.addCandlestickSeries({
                            upColor: '#26a69a',
                            downColor: '#ef5350',
                            borderVisible: false,
                            wickUpColor: '#26a69a',
                            wickDownColor: '#ef5350',
                        });
                        
                        // Añadir serie de volumen
                        const volumeSeries = chart.addHistogramSeries({
                            color: '#26a69a',
                            priceFormat: {
                                type: 'volume',
                            },
                            priceScaleId: '',
                            scaleMargins: {
                                top: 0.8,
                                bottom: 0,
                            },
                        });
                        
                        // Preparar datos para el gráfico
                        const candleData = chartData.candles.map(candle => ({
                            time: candle.time,
                            open: candle.open,
                            high: candle.high,
                            low: candle.low,
                            close: candle.close,
                        }));
                        
                        const volumeData = chartData.volumes.map(volume => ({
                            time: volume.time,
                            value: volume.value,
                            color: volume.color,
                        }));
                        
                        // Establecer datos en las series
                        candleSeries.setData(candleData);
                        volumeSeries.setData(volumeData);
                        
                        // Ajustar la vista para mostrar todos los datos
                        chart.timeScale().fitContent();
                        
                        return null;
                    }
                };
            ''')
        ]),
    ], className="analysis-page-container")
    
    return layout

def register_lw_chart_callbacks(app):
    """
    Registra los callbacks para la página de análisis técnico con lightweight-charts
    """
    @app.callback(
        Output('analysis-lw-chart-data', 'data'),
        [Input('analysis-lw-load-data-signal', 'data'), 
         Input('lw-real-time-update-interval', 'n_intervals')],
        [State('analysis-exchange-selector', 'value'),
         State('analysis-symbol-selector', 'value'),
         State('analysis-timeframe-selector', 'value'),
         State('real-time-update-toggle', 'value')]
    )
    def update_lw_chart_data(signal, n_intervals, exchange, symbol, timeframe, real_time):
        """Actualiza los datos del gráfico"""
        try:
            # Obtener datos OHLCV
            df = get_ohlcv_data(exchange=exchange, symbol=symbol, timeframe=timeframe, limit=100)
            
            if df is None or df.empty:
                return {}
            
            # Asegurarnos de que timestamp está presente como columna
            if 'timestamp' not in df.columns and isinstance(df.index, pd.DatetimeIndex):
                df = df.reset_index()  # Convertir el índice en una columna
                df.rename(columns={'index': 'timestamp'}, inplace=True)
            elif 'timestamp' not in df.columns:
                # Si no hay índice de tiempo, crear uno
                df['timestamp'] = pd.date_range(end=pd.Timestamp.now(), periods=len(df), freq='H')
            
            # Preparar datos para el gráfico
            chart_data = prepare_lw_chart_data(df)
            
            return chart_data
        except Exception as e:
            print(f"Error al actualizar datos del gráfico: {e}")
            return {}
    
    @app.callback(
        Output('lw-timeframe', 'data'),
        [Input('analysis-timeframe-selector', 'value')]
    )
    def update_timeframe(timeframe):
        """Actualiza el timeframe seleccionado"""
        return timeframe
    
    @app.callback(
        Output('lw-real-time-update-interval', 'disabled'),
        [Input('real-time-update-toggle', 'value')]
    )
    def toggle_real_time_updates(enabled):
        """Activa/desactiva la actualización en tiempo real"""
        return not enabled
    
    # Clientside callback para renderizar el gráfico
    app.clientside_callback(
        """
        function(chartData, timeframe) {
            return window.dash_clientside.clientside.renderLightweightChart(chartData, timeframe);
        }
        """,
        Output('lightweight-chart-container', 'children'),
        [Input('analysis-lw-chart-data', 'data'), Input('lw-timeframe', 'data')]
    )

def prepare_lw_chart_data(df):
    """
    Prepara los datos para el gráfico lightweight-charts
    """
    if df is None or df.empty:
        return {'candles': [], 'volumes': []}
    
    # Asegurarse de que el dataframe tiene las columnas correctas
    required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    if not all(col in df.columns for col in required_columns):
        print(f"Error: Faltan columnas en el dataframe. Columnas disponibles: {df.columns}")
        return {'candles': [], 'volumes': []}
    
    # Convertir timestamps a formato compatible con lightweight-charts
    candles = []
    volumes = []
    
    for _, row in df.iterrows():
        # Para las velas
        timestamp = row['timestamp']
        # Convertir timestamp si es necesario
        if isinstance(timestamp, (int, float)):
            # Si es un timestamp en segundos, convertir a milisegundos
            if timestamp < 1e12:  # Asumimos que es en segundos
                timestamp *= 1000
            time_value = int(timestamp)
        else:
            # Si es datetime, convertir a timestamp en milisegundos
            time_value = int(pd.Timestamp(timestamp).timestamp() * 1000)
        
        # Crear objeto de vela
        candle = {
            'time': time_value,
            'open': float(row['open']),
            'high': float(row['high']),
            'low': float(row['low']),
            'close': float(row['close'])
        }
        candles.append(candle)
        
        # Crear objeto de volumen con color
        volume_color = '#26a69a' if row['close'] >= row['open'] else '#ef5350'
        volume = {
            'time': time_value,
            'value': float(row['volume']),
            'color': volume_color
        }
        volumes.append(volume)
    
    return {
        'candles': candles,
        'volumes': volumes
    }
