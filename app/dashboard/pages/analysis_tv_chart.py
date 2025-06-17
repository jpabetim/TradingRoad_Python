"""
Componente de gráfico de TradingView Lightweight Charts para la aplicación
"""
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import json
import os

# Definición del componente de TradingView Chart para ser insertado en análisis
def create_tv_chart_component(height=700):
    """
    Crea el componente de gráfico de TradingView Lightweight Charts con aspecto profesional
    
    Args:
        height: Altura del gráfico en píxeles
        
    Returns:
        Componente HTML con el gráfico de TradingView avanzado
    """
    return html.Div([
        # Cabecera con controles adicionales, similar a las imágenes de referencia
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
                                {"label": "Bybit", "value": "bybit"},
                                {"label": "Coinbase", "value": "coinbase"},
                            ],
                            value="binance_futures",
                            className="tv-dropdown dark-dropdown",
                        ),
                    ]),
                ], width=3),
                
                # Columna central: Par de trading/Símbolo
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
                                dbc.Button("1M", id="tv-tf-1m", color="dark", size="sm", outline=True, className="tv-tf-button"),
                                dbc.Button("3M", id="tv-tf-3m", color="dark", size="sm", outline=True, className="tv-tf-button"),
                                dbc.Button("5M", id="tv-tf-5m", color="dark", size="sm", outline=True, className="tv-tf-button"),
                                dbc.Button("15M", id="tv-tf-15m", color="dark", size="sm", outline=True, className="tv-tf-button"),
                                dbc.Button("1H", id="tv-tf-1h", color="primary", size="sm", className="tv-tf-button"),
                                dbc.Button("4H", id="tv-tf-4h", color="dark", size="sm", outline=True, className="tv-tf-button"),
                                dbc.Button("1D", id="tv-tf-1d", color="dark", size="sm", outline=True, className="tv-tf-button"),
                                dbc.Button("1W", id="tv-tf-1w", color="dark", size="sm", outline=True, className="tv-tf-button"),
                            ],
                        ),
                    ]),
                ], width=6),
            ], className="mb-2"),
            
            # Botón para cambiar tema claro/oscuro y mostrar/ocultar panel
            dbc.Row([
                dbc.Col(html.Div(), width=9),
                dbc.Col([
                    dbc.ButtonGroup([
                        dbc.Button([
                            html.I(className="fas fa-moon"), " Light Mode"
                        ], id="tv-theme-toggle", color="dark", size="sm", className="me-1"),
                        dbc.Button([
                            html.I(className="fas fa-columns"), " Hide Panel"
                        ], id="tv-panel-toggle", color="dark", size="sm")
                    ])
                ], width=3),
            ], className="mb-2"),
        ], className="tv-controls px-3 py-2"),

        # Contenedor principal dividido en dos columnas
        dbc.Row([
            # Columna izquierda: Gráfico principal
            dbc.Col([
                html.Div(
                    id="tradingview-chart-container",
                    style={"width": "100%", "height": f"{height}px", "position": "relative"}
                ),
            ], id="tv-chart-col", width=9, className="tv-chart-col"),
            
            # Columna derecha: Panel lateral (controles y resultados AI)
            dbc.Col([
                html.Div([
                    html.H5("Market Controls", className="text-light mb-3"),
                    
                    # Configuración de visualización
                    html.Div([
                        html.H6(className="text-light mb-2 d-flex align-items-center",
                               children=[html.I(className="fas fa-cog me-2"), "Display Settings"]),
                        dbc.Collapse([
                            dbc.CheckboxGroup(
                                id="tv-indicator-toggles",
                                options=[
                                    {"label": "MA-20", "value": "sma20"},
                                    {"label": "MA-50", "value": "sma50"},
                                    {"label": "MA-200", "value": "sma200"},
                                    {"label": "RSI", "value": "rsi"},
                                    {"label": "Volume", "value": "volume"},
                                    {"label": "Fibonacci", "value": "fib"},
                                ],
                                value=["sma20", "sma50", "volume"],
                                inline=True,
                                className="tv-checkbox-group"
                            ),
                        ], id="display-settings-collapse", is_open=True),
                    ], className="mb-4 tv-section"),
                    
                    # Sección de resultados AI
                    html.Div([
                        html.H5("AI Analysis Results", className="text-light mb-3"),
                        html.Hr(className="mt-0 mb-3 bg-secondary"),
                        
                        # Escenario principal
                        html.Div([
                            html.H6("Primary Scenario", className="text-light"),
                            html.Div([
                                html.P(
                                    id="tv-ai-scenario",
                                    children=["Escenario Principal: Bajista hacia Liquidez Inferior"],
                                    className="mb-2 fw-bold"
                                ),
                                html.P(
                                    id="tv-ai-description",
                                    children=["El precio se encuentra en un retroceso dentro de una estructura bajista de 4H. Se espera que continue hacia la liquidez por debajo de $2360 después de un posible test de la EMA de 200 a $2600."],
                                    className="mb-2 small"
                                ),
                                html.P(["Invalidación: Cierre de vela de 4H por encima de $2715 invalidaría este escenario."], className="mb-2 small fst-italic"),
                                
                                html.Div([
                                    html.Strong("Associated Setup: "),
                                    html.Span("CORTO", id="tv-ai-setup", className="text-danger")
                                ], className="d-flex small"),
                                
                                html.Div([
                                    html.Strong("Type: "),
                                    html.Span("CORTO", id="tv-ai-type")
                                ], className="d-flex small"),
                                
                                html.Div([
                                    html.Strong("Entry Condition: "),
                                    html.Span("Entrar en corto al testear el Bearish OB 4H (2450-2480), idealmente con confirmación de ChoCh bajista en 4H", id="tv-ai-entry")
                                ], className="d-flex small flex-wrap")
                            ], className="tv-ai-section p-3")
                        ]),
                    ], className="tv-ai-container")
                ], className="tv-sidebar p-3")
            ], id="tv-sidebar-col", width=3, className="tv-sidebar-col"),
        ]),
        
        # Recursos para TradingView Lightweight Charts
        html.Script(
            src="https://unpkg.com/lightweight-charts@4.1.0/dist/lightweight-charts.standalone.production.js",
            id="tv-script"
        ),
        
        # Estilos personalizados para el componente
        html.Style(
            """
            .tv-controls {
                background-color: #131722;
                border-bottom: 1px solid #2a2e39;
            }
            .tv-chart-col {
                border-right: 1px solid #2a2e39;
                padding-right: 0;
                padding-left: 0;
            }
            .tv-sidebar-col {
                background-color: #131722;
                padding: 0;
            }
            .tv-sidebar {
                height: 100%;
            }
            .tv-dropdown .Select-control {
                background-color: #2a2e39;
                border-color: #2a2e39;
                color: #d1d4dc;
            }
            .tv-input {
                background-color: #2a2e39;
                border-color: #2a2e39;
                color: #d1d4dc;
            }
            .tv-tf-button {
                padding: 0.2rem 0.5rem;
                margin-right: 2px;
            }
            .tv-ai-section {
                background-color: #1c2030;
                border-radius: 4px;
                border: 1px solid #2a2e39;
            }
            .tv-checkbox-group .form-check {
                margin-right: 12px;
            }
            .tv-checkbox-group .form-check-label {
                color: #d1d4dc;
                font-size: 0.875rem;
            }
            """
        ),
        
        # Almacenamiento de datos para el gráfico
        dcc.Store(id="tv-chart-data", data=None),
        dcc.Store(id="tv-timeframe", data="1h"),
        dcc.Store(id="tv-theme", data="dark"),
        dcc.Store(id="tv-panel-visible", data=True),
        
        # Script para inicializar y manipular el gráfico
        html.Script(
            id="tv-init-script",
            children="""
            document.addEventListener('DOMContentLoaded', function() {
                // Variables globales para el estado
                window.tvChartState = {
                    timeframe: '1h',
                    symbol: 'ETHUSDT',
                    exchange: 'binance_futures',
                    indicators: ['sma20', 'sma50', 'volume'],
                    theme: 'dark',
                    panelVisible: true
                };
                
                // Crear el gráfico
                const chartElement = document.getElementById('tradingview-chart-container');
                
                // Verificar si el elemento existe en el DOM
                if (!chartElement) {
                    console.error('Elemento para TradingView chart no encontrado');
                    return;
                }
                
                // Configuración del gráfico
                let chartOptions = {
                    width: chartElement.clientWidth,
                    height: chartElement.clientHeight,
                    layout: {
                        background: { color: '#131722' },
                        textColor: '#d1d4dc',
                        fontSize: 12,
                    },
                    grid: {
                        vertLines: { color: 'rgba(42, 46, 57, 0.6)' },
                        horzLines: { color: 'rgba(42, 46, 57, 0.6)' },
                    },
                    crosshair: {
                        mode: LightweightCharts.CrosshairMode.Normal,
                        vertLine: {
                            color: 'rgba(224, 227, 235, 0.1)',
                            width: 1,
                            style: 0,
                            labelBackgroundColor: '#2a2e39',
                        },
                        horzLine: {
                            color: 'rgba(224, 227, 235, 0.1)',
                            width: 1,
                            style: 0,
                            labelBackgroundColor: '#2a2e39',
                        },
                    },
                    rightPriceScale: {
                        borderColor: 'rgba(197, 203, 206, 0.8)',
                        scaleMargins: {
                            top: 0.1,
                            bottom: 0.2,
                        },
                    },
                    timeScale: {
                        borderColor: 'rgba(197, 203, 206, 0.8)',
                        timeVisible: true,
                        secondsVisible: false,
                    },
                    watermark: {
                        visible: true,
                        fontSize: 40,
                        horzAlign: 'center',
                        vertAlign: 'center',
                        color: 'rgba(224, 227, 235, 0.05)',
                        text: 'TradingRoad',
                    },
                };
                
                // Inicializar el gráfico
                window.chart = LightweightCharts.createChart(chartElement, chartOptions);
                
                // Crear la serie de velas japonesas
                window.candleSeries = window.chart.addCandlestickSeries({
                    upColor: '#26a69a',
                    downColor: '#ef5350',
                    borderDownColor: '#ef5350',
                    borderUpColor: '#26a69a',
                    wickDownColor: '#ef5350',
                    wickUpColor: '#26a69a',
                });
                
                // Crear series para indicadores
                window.sma20Series = window.chart.addLineSeries({
                    color: 'rgba(255, 255, 0, 1)',
                    lineWidth: 1.5,
                    title: 'MA-20',
                    priceLineVisible: false,
                });
                
                window.sma50Series = window.chart.addLineSeries({
                    color: 'rgba(255, 140, 0, 1)',
                    lineWidth: 1.5,
                    title: 'MA-50',
                    priceLineVisible: false,
                });
                
                window.sma200Series = window.chart.addLineSeries({
                    color: 'rgba(144, 238, 144, 1)',
                    lineWidth: 1.5,
                    title: 'MA-200',
                    priceLineVisible: false,
                });
                
                // Agregar serie de volúmenes
                window.volumeSeries = window.chart.addHistogramSeries({
                    color: '#26a69a',
                    priceFormat: {
                        type: 'volume',
                    },
                    priceScaleId: 'volume',
                    scaleMargins: {
                        top: 0.8,
                        bottom: 0,
                    },
                });
                
                // Agregar serie para RSI (oculta por defecto)
                window.rsiSeries = window.chart.addLineSeries({
                    color: '#ff9900',
                    lineWidth: 1.5,
                    title: 'RSI',
                    priceLineVisible: false,
                    visible: false,
                    priceScaleId: 'rsi',
                    scaleMargins: {
                        top: 0.8,
                        bottom: 0,
                    },
                });
                
                // Funciones de respuesta al tamaño
                function handleResize() {
                    window.chart.applyOptions({
                        width: chartElement.clientWidth,
                        height: chartElement.clientHeight
                    });
                }
                
                // Respuesta a cambios de tamaño
                const resizeObserver = new ResizeObserver(entries => {
                    window.setTimeout(() => handleResize(), 100);
                });
                resizeObserver.observe(chartElement);
                
                // Función para cambiar el tema del gráfico
                window.toggleChartTheme = function(theme) {
                    const darkTheme = {
                        backgroundColor: '#131722',
                        textColor: '#d1d4dc',
                        gridColor: 'rgba(42, 46, 57, 0.6)'
                    };
                    
                    const lightTheme = {
                        backgroundColor: '#ffffff',
                        textColor: '#131722',
                        gridColor: 'rgba(42, 46, 57, 0.2)'
                    };
                    
                    const selectedTheme = theme === 'dark' ? darkTheme : lightTheme;
                    
                    window.chart.applyOptions({
                        layout: {
                            background: { color: selectedTheme.backgroundColor },
                            textColor: selectedTheme.textColor,
                        },
                        grid: {
                            vertLines: { color: selectedTheme.gridColor },
                            horzLines: { color: selectedTheme.gridColor },
                        },
                    });
                    
                    window.tvChartState.theme = theme;
                };
                
                // Función para mostrar/ocultar indicadores
                window.toggleIndicator = function(indicator, visible) {
                    switch(indicator) {
                        case 'sma20':
                            window.sma20Series.applyOptions({ visible: visible });
                            break;
                        case 'sma50':
                            window.sma50Series.applyOptions({ visible: visible });
                            break;
                        case 'sma200':
                            window.sma200Series.applyOptions({ visible: visible });
                            break;
                        case 'rsi':
                            window.rsiSeries.applyOptions({ visible: visible });
                            break;
                        case 'volume':
                            window.volumeSeries.applyOptions({ visible: visible });
                            break;
                        case 'fib':
                            // Implementar niveles fibonacci si se requiere
                            break;
                    }
                };
                
                // Función para cargar datos
                window.loadChartData = function(data) {
                    if (!data) return;
                    
                    // Cargar datos de velas
                    window.candleSeries.setData(data.candles);
                    
                    // Cargar datos de SMA
                    if (data.sma20 && data.sma20.length > 0) {
                        window.sma20Series.setData(data.sma20);
                    }
                    
                    if (data.sma50 && data.sma50.length > 0) {
                        window.sma50Series.setData(data.sma50);
                    }
                    
                    if (data.sma200 && data.sma200.length > 0) {
                        window.sma200Series.setData(data.sma200);
                    }
                    
                    // Cargar datos de volúmenes si están disponibles
                    if (data.volumes && data.volumes.length > 0) {
                        window.volumeSeries.setData(data.volumes);
                    }
                    
                    // Cargar datos de RSI si están disponibles
                    if (data.rsi && data.rsi.length > 0) {
                        window.rsiSeries.setData(data.rsi);
                    }
                    
                    // Ajustar el rango visible para ver los datos
                    window.chart.timeScale().fitContent();
                }
                
                // Función para cambiar el timeframe
                window.changeTimeframe = function(timeframe) {
                    window.tvChartState.timeframe = timeframe;
                    
                    // Modificar los botones de timeframe para reflejar la selección
                    const allButtons = [
                        'tv-tf-1m', 'tv-tf-3m', 'tv-tf-5m', 'tv-tf-15m',
                        'tv-tf-1h', 'tv-tf-4h', 'tv-tf-1d', 'tv-tf-1w'
                    ];
                    
                    allButtons.forEach(buttonId => {
                        const button = document.getElementById(buttonId);
                        if (button) {
                            // Convertir el ID del botón al formato del timeframe
                            const buttonTimeframe = buttonId.replace('tv-tf-', '').toLowerCase();
                            
                            // Comparar con el timeframe actual
                            if (buttonTimeframe === timeframe) {
                                button.classList.remove('btn-outline-dark');
                                button.classList.add('btn-primary');
                            } else {
                                button.classList.remove('btn-primary');
                                button.classList.add('btn-outline-dark');
                            }
                        }
                    });
                }
                
                // Función para cambiar el símbolo y exchange
                window.changeSymbol = function(symbol, exchange) {
                    window.tvChartState.symbol = symbol;
                    window.tvChartState.exchange = exchange;
                }
                
                // Función para mostrar/ocultar el panel lateral
                window.togglePanel = function(visible) {
                    const chartCol = document.getElementById('tv-chart-col');
                    const sidebarCol = document.getElementById('tv-sidebar-col');
                    
                    if (chartCol && sidebarCol) {
                        if (visible) {
                            chartCol.className = chartCol.className.replace('col-md-12', 'col-md-9');
                            sidebarCol.style.display = 'block';
                        } else {
                            chartCol.className = chartCol.className.replace('col-md-9', 'col-md-12');
                            sidebarCol.style.display = 'none';
                        }
                        
                        // Actualizar el botón
                        const panelToggle = document.getElementById('tv-panel-toggle');
                        if (panelToggle) {
                            const icon = panelToggle.querySelector('i');
                            const text = panelToggle.textContent.replace(icon ? icon.outerHTML : '', '').trim();
                            panelToggle.innerHTML = visible ? 
                                '<i class="fas fa-columns"></i> Hide Panel' : 
                                '<i class="fas fa-columns"></i> Show Panel';
                        }
                        
                        // Forzar un redimensionamiento del gráfico
                        setTimeout(() => {
                            if (window.chart) {
                                window.chart.applyOptions({
                                    width: chartElement.clientWidth,
                                    height: chartElement.clientHeight
                                });
                            }
                        }, 300);
                    }
                    
                    window.tvChartState.panelVisible = visible;
                }
                
                // Cargar datos iniciales si están disponibles en el store
                const tvChartDataStore = document.getElementById('tv-chart-data');
                if (tvChartDataStore && tvChartDataStore.hasAttribute('data-dash-store') && tvChartDataStore.getAttribute('data-dash-store') !== 'null') {
                    try {
                        const initialData = JSON.parse(tvChartDataStore.getAttribute('data-dash-store'));
                        window.loadChartData(initialData);
                    } catch (e) {
                        console.error('Error loading initial data:', e);
                    }
                }
            });
            
            // Funciones Clientside para Dash
            if (window.dash_clientside) {
                window.dash_clientside.no_update = window.dash_clientside.no_update || function() {};
                window.dash_clientside.clientside = window.dash_clientside.clientside || {};
                
                // Actualizar datos del gráfico
                window.dash_clientside.clientside.updateTvChart = function(data) {
                    if (!data || !window.loadChartData) return window.dash_clientside.no_update;
                    window.loadChartData(data);
                    return window.dash_clientside.no_update;
                };
                
                // Cambiar timeframe
                window.dash_clientside.clientside.changeTimeframe = function(n_clicks_1m, n_clicks_3m, n_clicks_5m, n_clicks_15m, n_clicks_1h, n_clicks_4h, n_clicks_1d, n_clicks_1w, current) {
                    const ctx = window.dash_clientside.callback_context;
                    if (!ctx.triggered) return current || '1h';
                    
                    const id = ctx.triggered[0].prop_id.split('.')[0];
                    if (!id) return current || '1h';
                    
                    const mapping = {
                        'tv-tf-1m': '1m',
                        'tv-tf-3m': '3m',
                        'tv-tf-5m': '5m',
                        'tv-tf-15m': '15m',
                        'tv-tf-1h': '1h',
                        'tv-tf-4h': '4h',
                        'tv-tf-1d': '1d',
                        'tv-tf-1w': '1w'
                    };
                    
                    if (mapping[id]) {
                        if (window.changeTimeframe) window.changeTimeframe(mapping[id]);
                        return mapping[id];
                    }
                    
                    return current || '1h';
                };
                
                // Cambiar tema
                window.dash_clientside.clientside.toggleTheme = function(n_clicks, current) {
                    if (!n_clicks) return current || 'dark';
                    
                    const newTheme = current === 'dark' ? 'light' : 'dark';
                    if (window.toggleChartTheme) window.toggleChartTheme(newTheme);
                    
                    // Actualizar el texto del botón
                    const themeToggle = document.getElementById('tv-theme-toggle');
                    if (themeToggle) {
                        themeToggle.innerHTML = newTheme === 'dark' ? 
                            '<i class="fas fa-moon"></i> Light Mode' : 
                            '<i class="fas fa-sun"></i> Dark Mode';
                    }
                    
                    return newTheme;
                };
                
                // Mostrar/ocultar panel
                window.dash_clientside.clientside.togglePanel = function(n_clicks, current) {
                    if (n_clicks === undefined || n_clicks === null) return current;
                    
                    const newState = !current;
                    if (window.togglePanel) window.togglePanel(newState);
                    
                    return newState;
                };
            }
            """
        )
    ])

# Función para preparar datos para el gráfico
def prepare_tv_chart_data(df):
    """
    Prepara datos en el formato esperado por TradingView Lightweight Charts
    
    Args:
        df: DataFrame con datos OHLCV
        
    Returns:
        dict: Datos formateados para TradingView con indicadores avanzados
    """
    if df is None or df.empty:
        return None
    
    # Convertir dataframe a formato de TV Charts
    candles = []
    volumes = []
    
    # Cálculo de RSI (14 períodos)
    try:
        # Calcular RSI - método estándar
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        
        rs = avg_gain / avg_loss.replace(0, 0.001)  # Evitar división por cero
        df['rsi'] = 100 - (100 / (1 + rs))
    except Exception as e:
        print(f"Error calculando RSI: {str(e)}")
        df['rsi'] = float('nan')
    
    # Procesar cada fila para crear candles y volúmenes
    for idx, row in df.iterrows():
        # Convertir timestamp a formato Unix en segundos
        time_str = None
        if isinstance(row['timestamp'], pd.Timestamp):
            time_str = int(row['timestamp'].timestamp())
        else:
            # Si ya es string, intentar convertirlo
            try:
                if isinstance(row['timestamp'], str):
                    time_str = int(pd.Timestamp(row['timestamp']).timestamp())
                else:
                    time_str = int(row['timestamp'])
            except:
                time_str = row['timestamp']
            
        # Crear objeto candle
        candle = {
            'time': time_str,
            'open': float(row['open']),
            'high': float(row['high']),
            'low': float(row['low']),
            'close': float(row['close'])
        }
        candles.append(candle)
        
        # Crear objeto volumen
        if 'volume' in row:
            volume = {
                'time': time_str,
                'value': float(row['volume']),
                'color': '#26a69a' if row['close'] >= row['open'] else '#ef5350'
            }
            volumes.append(volume)
    
    # Calcular indicadores
    sma20 = []
    sma50 = []
    sma200 = []
    rsi_data = []
    
    # SMA 20
    if len(df) >= 20:
        df['sma20'] = df['close'].rolling(window=20).mean()
        for idx, row in df.iterrows():
            if not pd.isna(row['sma20']):
                time_str = None
                if isinstance(row['timestamp'], pd.Timestamp):
                    time_str = int(row['timestamp'].timestamp())
                else:
                    try:
                        if isinstance(row['timestamp'], str):
                            time_str = int(pd.Timestamp(row['timestamp']).timestamp())
                        else:
                            time_str = int(row['timestamp'])
                    except:
                        time_str = row['timestamp']
                    
                sma20.append({
                    'time': time_str,
                    'value': float(row['sma20'])
                })
    
    # SMA 50
    if len(df) >= 50:
        df['sma50'] = df['close'].rolling(window=50).mean()
        for idx, row in df.iterrows():
            if not pd.isna(row['sma50']):
                time_str = None
                if isinstance(row['timestamp'], pd.Timestamp):
                    time_str = int(row['timestamp'].timestamp())
                else:
                    try:
                        if isinstance(row['timestamp'], str):
                            time_str = int(pd.Timestamp(row['timestamp']).timestamp())
                        else:
                            time_str = int(row['timestamp'])
                    except:
                        time_str = row['timestamp']
                    
                sma50.append({
                    'time': time_str,
                    'value': float(row['sma50'])
                })
    
    # SMA 200
    if len(df) >= 200:
        df['sma200'] = df['close'].rolling(window=200).mean()
        for idx, row in df.iterrows():
            if not pd.isna(row['sma200']):
                time_str = None
                if isinstance(row['timestamp'], pd.Timestamp):
                    time_str = int(row['timestamp'].timestamp())
                else:
                    try:
                        if isinstance(row['timestamp'], str):
                            time_str = int(pd.Timestamp(row['timestamp']).timestamp())
                        else:
                            time_str = int(row['timestamp'])
                    except:
                        time_str = row['timestamp']
                    
                sma200.append({
                    'time': time_str,
                    'value': float(row['sma200'])
                })
    
    # RSI
    for idx, row in df.iterrows():
        if not pd.isna(row.get('rsi', None)):
            time_str = None
            if isinstance(row['timestamp'], pd.Timestamp):
                time_str = int(row['timestamp'].timestamp())
            else:
                try:
                    if isinstance(row['timestamp'], str):
                        time_str = int(pd.Timestamp(row['timestamp']).timestamp())
                    else:
                        time_str = int(row['timestamp'])
                except:
                    time_str = row['timestamp']
                
            rsi_data.append({
                'time': time_str,
                'value': float(row['rsi'])
            })
    
    # Retornar datos formateados
    return {
        'candles': candles,
        'volumes': volumes,
        'sma20': sma20,
        'sma50': sma50,
        'sma200': sma200,
        'rsi': rsi_data
    }

# Callback para actualizar los datos del gráfico
def register_tv_chart_callbacks(app):
    """
    Registra los callbacks necesarios para el gráfico de TradingView y sus controles
    
    Args:
        app: Aplicación Dash
    """
    # Callback para actualizar datos del gráfico (permite actualización en tiempo real)
    @app.callback(
        Output('tv-chart-data', 'data'),
        [Input('analysis-load-data-signal', 'data'),
         Input('real-time-update-interval', 'n_intervals')],
        [State('analysis-chart-data', 'data'),
         State('real-time-update-toggle', 'value')]
    )
    def update_tv_chart_data(signal, n_intervals, chart_data, auto_update):
        """Actualiza los datos para el gráfico de TradingView"""
        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
        
        # Solo actualizar si viene de la señal de carga o de un intervalo cuando auto_update está activo
        if triggered_id == 'real-time-update-interval' and not auto_update:
            return dash.no_update
        
        if chart_data is None:
            return None
        
        try:
            # Convertir los datos a DataFrame para poder procesarlos
            df = pd.DataFrame(chart_data)
            
            # Preparar datos para TV Charts incluyendo todos los indicadores
            tv_data = prepare_tv_chart_data(df)
            
            return tv_data
        except Exception as e:
            print(f"Error al procesar datos para TradingView: {str(e)}")
            return None
    
    # Callback para cambiar el timeframe
    app.clientside_callback(
        """function(n_clicks_1m, n_clicks_3m, n_clicks_5m, n_clicks_15m, n_clicks_1h, n_clicks_4h, n_clicks_1d, n_clicks_1w, current) {
            return window.dash_clientside.clientside.changeTimeframe(n_clicks_1m, n_clicks_3m, n_clicks_5m, n_clicks_15m, n_clicks_1h, n_clicks_4h, n_clicks_1d, n_clicks_1w, current);
        }""",
        Output('tv-timeframe', 'data'),
        [Input('tv-tf-1m', 'n_clicks'),
         Input('tv-tf-3m', 'n_clicks'),
         Input('tv-tf-5m', 'n_clicks'),
         Input('tv-tf-15m', 'n_clicks'),
         Input('tv-tf-1h', 'n_clicks'),
         Input('tv-tf-4h', 'n_clicks'),
         Input('tv-tf-1d', 'n_clicks'),
         Input('tv-tf-1w', 'n_clicks')],
        [State('tv-timeframe', 'data')],
        prevent_initial_call=True
    )
    
    # Callback para cambiar tema
    app.clientside_callback(
        """function(n_clicks, current) {
            return window.dash_clientside.clientside.toggleTheme(n_clicks, current);
        }""",
        Output('tv-theme', 'data'),
        [Input('tv-theme-toggle', 'n_clicks')],
        [State('tv-theme', 'data')],
        prevent_initial_call=True
    )
    
    # Callback para mostrar/ocultar panel
    app.clientside_callback(
        """function(n_clicks, current) {
            return window.dash_clientside.clientside.togglePanel(n_clicks, current);
        }""",
        Output('tv-panel-visible', 'data'),
        [Input('tv-panel-toggle', 'n_clicks')],
        [State('tv-panel-visible', 'data')],
        prevent_initial_call=True
    )
    
    # Callback para gestionar indicadores
    @app.callback(
        Output('tradingview-chart-container', 'children'),
        Input('tv-indicator-toggles', 'value'),
        prevent_initial_call=True
    )
    def toggle_indicators(indicators):
        # Este callback es sólo para activar una llamada JavaScript
        # Los cambios reales los hace el JavaScript via clientside
        return dash.no_update
    
    # Callback para actualizar datos basado en el exchange y symbol
    @app.callback(
        Output('analysis-load-data-signal', 'data'),
        [Input('tv-exchange-dropdown', 'value'),
         Input('tv-symbol-input', 'value'),
         Input('tv-timeframe', 'data')],
        prevent_initial_call=True
    )
    def load_symbol_data(exchange, symbol, timeframe):
        if not exchange or not symbol or not timeframe:
            return dash.no_update
            
        # Devolver una señal con los nuevos parámetros para que el callback de datos lo procese
        return {'exchange': exchange, 'symbol': symbol, 'timeframe': timeframe, 'timestamp': int(time.time())}
    
    # Registrar callback clientside para la actualización del gráfico
    app.clientside_callback(
        """function(data) {
            if (!data || !window.loadChartData) return window.dash_clientside.no_update;
            window.loadChartData(data);
            return window.dash_clientside.no_update;
        }""",
        Output('tradingview-chart-container', 'n_clicks'),
        Input('tv-chart-data', 'data'),
        prevent_initial_call=True
    )
