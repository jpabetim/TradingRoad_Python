import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import plotly.subplots as sp
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta

# Importamos funciones de utilidad
from app.utils.market_data import MarketDataClient  # Importamos la clase en lugar de la función
from app.utils.technical_analysis import generate_analysis  # Usamos la función que sí existe

# Funciones auxiliares y definición del layout se mantienen fuera de register_callbacks

def register_callbacks(app):
    """Registrar los callbacks para la página de análisis"""
    
    # Callback para mostrar/ocultar el panel de análisis
    @app.callback(
        Output("analysis-panel", "style"),
        Output("main-chart-container", "style"),
        [Input("load-data-button", "n_clicks"),
         Input("close-analysis-panel", "n_clicks"),
         Input("show-ai-button", "n_clicks")],
        [State("analysis-panel", "style"),
         State("main-chart-container", "style")],
        prevent_initial_call=True
    )
    def toggle_analysis_panel(load_clicks, close_clicks, show_clicks, panel_style, main_container_style):
        ctx = dash.callback_context
        if not ctx.triggered:
            return panel_style, main_container_style
        
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        panel_visible = panel_style.get("display") != "none"
        
        # Copiar los estilos para no modificar los originales
        new_panel_style = dict(panel_style)
        new_container_style = dict(main_container_style)
        
        # Mostrar u ocultar según el botón pulsado
        if button_id in ["load-data-button", "show-ai-button"]:
            new_panel_style["display"] = "block"
            new_container_style["marginLeft"] = "350px"
        elif button_id == "close-analysis-panel":
            new_panel_style["display"] = "none"
            new_container_style["marginLeft"] = "0px"
        
        return new_panel_style, new_container_style
    
    # Callback para activar/desactivar la actualización en tiempo real
    @app.callback(
        Output("chart-interval", "disabled"),
        [Input("real-time-update", "value")],
        prevent_initial_call=True
    )
    def toggle_interval(active):
        return not active
    
    # Callback para actualizar el gráfico principal con todas las características avanzadas
    @app.callback(
        [Output("trading-chart", "figure", allow_duplicate=True),
         Output("analysis-ai-content", "children")],
        [Input("load-data-button", "n_clicks"),
         Input("chart-interval", "n_intervals"),
         Input("tf-5m", "n_clicks"),
         Input("tf-15m", "n_clicks"),
         Input("tf-30m", "n_clicks"),
         Input("tf-1h", "n_clicks"),
         Input("tf-4h", "n_clicks"),
         Input("tf-1d", "n_clicks")],
        [State("exchange-selector", "value"),
         State("pair-selector", "value"),
         State("sma-checklist", "value"),
         State("ema-checklist", "value"),
         State("other-indicators-checklist", "value"),
         State("real-time-update", "active")],
        prevent_initial_call=True
    )
    def update_trading_chart(n_clicks, n_intervals, tf_5m, tf_15m, tf_30m, tf_1h, tf_4h, tf_1d, exchange, pair, sma_periods, ema_periods, other_indicators, real_time_active):
        """Actualiza el gráfico de análisis técnico con todos los indicadores"""
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update, dash.no_update
        
        # Determinar el timeframe basado en los botones
        timeframe = "1h"  # valor por defecto
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
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
        
        # Crear una figura para el análisis técnico avanzado (pueden ser datos reales o simulados)
        indicators = {
            "sma": sma_periods if sma_periods else [],
            "ema": ema_periods if ema_periods else [],
            "other": other_indicators if other_indicators else []
        }
        
        fig = create_advanced_analysis_chart(pair, timeframe, exchange, "dark", indicators)
        
        # Generar análisis de IA para el par seleccionado
        ai_content = generate_ai_analysis_content(timeframe, pair)
        
        return fig, ai_content

# Definición de todas las funciones antes del layout
def create_empty_chart(analysis_type, theme="dark"):
    """Crear un gráfico vacío para mostrar inicialmente con mayor interactividad"""
    # Crear una figura con subplots para poder añadir volumen debajo
    fig = sp.make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.02, row_heights=[0.8, 0.2])
    
    # Configurar colores según tema
    if theme == "dark":
        paper_bgcolor = "#131722"
        plot_bgcolor = "#131722"
        font_color = "white"
        grid_color = "rgba(255, 255, 255, 0.1)"
    else:
        paper_bgcolor = "#FFFFFF"
        plot_bgcolor = "#F5F5F5"
        font_color = "#333333"
        grid_color = "rgba(150, 150, 150, 0.2)"
    
    # Actualizar el layout para mayor interactividad
    fig.update_layout(
        title=f"Seleccione un activo y periodo para ver el análisis {analysis_type}",
        paper_bgcolor=paper_bgcolor,
        plot_bgcolor=plot_bgcolor,
        font=dict(color=font_color),
        xaxis_title="Fecha/Hora",
        yaxis_title="Precio",
        yaxis2_title="Volumen",
        height=650,  # Mayor altura para mejor visualización
        margin=dict(l=10, r=60, t=40, b=10),  # Márgenes reducidos para maximizar espacio
        legend=dict(orientation="h", y=1.02),  # Leyenda horizontal arriba
        xaxis=dict(
            showgrid=True,
            gridcolor=grid_color,
            rangeslider=dict(visible=False),  # Sin rangeslider para maximizar espacio
            type="date"
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=grid_color,
            side="right"  # Escala de precios a la derecha como solicitado
        ),
        yaxis2=dict(
            showgrid=False,
            side="right"  # Volumen también a la derecha
        ),
        hoverlabel=dict(
            bgcolor="rgba(0,0,0,0.8)",
            font_size=12,
            font_family="Roboto"
        ),
    )
    
    # Habilitar todas las herramientas de interacción
    fig.update_layout(
        modebar=dict(orientation='v'),
        dragmode="zoom",  # Modo zoom por defecto
        hovermode="closest"
    )
    
    return fig

def create_correlation_heatmap(theme="dark"):
    """Crear un heatmap de correlación entre varios activos con mayor interactividad"""
    # Crear datos de ejemplo para correlación - incluir más activos
    np.random.seed(42)
    assets = ["BTC", "ETH", "BNB", "XRP", "ADA", "SOL", "DOT", "AVAX", "MATIC", "LINK", "UNI", "LTC"]
    n_assets = len(assets)
    
    # Crear una matriz de correlación aleatoria pero realista
    base = np.random.rand(n_assets, n_assets)
    corr = (base + base.T) / 2  # Hacer simétrica
    np.fill_diagonal(corr, 1)  # Diagonal de 1's
    
    # Asegurar que los valores estén entre -1 y 1, con tendencia a valores positivos para criptomonedas
    corr = (corr * 1.2) - 0.2
    corr = np.clip(corr, -1, 1)
    
    # Elegir colores basados en el tema
    if theme == "dark":
        paper_bgcolor = "#131722"
        plot_bgcolor = "#131722"
        font_color = "white"
        colorscale = "RdBu_r"
    else:
        paper_bgcolor = "#FFFFFF"
        plot_bgcolor = "#F5F5F5"
        font_color = "#333333"
        colorscale = "RdBu"
    
    # Crear figura de heatmap con mejoras visuales
    fig = px.imshow(
        corr,
        x=assets,
        y=assets,
        color_continuous_scale=colorscale,
        labels=dict(x="Activo", y="Activo", color="Correlación"),
        text_auto=True,  # Mostrar valores en cada celda
        aspect="auto"    # Ajustar aspecto automáticamente
    )
    
    fig.update_layout(
        title="Correlación entre activos",
        paper_bgcolor=paper_bgcolor,
        plot_bgcolor=plot_bgcolor,
        font=dict(color=font_color),
        height=500,
        margin=dict(l=10, r=10, t=40, b=10),
        hoverlabel=dict(
            bgcolor="rgba(0,0,0,0.8)",
            font_size=12,
            font_family="Roboto"
        )
    )
    
    # Mejoras para la visualización de datos
    fig.update_traces(
        hoverongaps=False,
        hovertemplate="%{y} - %{x}<br>Correlación: %{z:.2f}<extra></extra>",
        texttemplate="%{z:.2f}",
        textfont=dict(size=10)
    )
    
    return fig

def create_volatility_chart(timeframe="1h", pair="BTC/USDT", theme="dark"):
    
    # En un entorno real, aquí obtendríamos datos históricos reales
    # Para este ejemplo, creamos datos simulados
    
    # Crear datos de tiempo para los últimos 30 días
    dates = pd.date_range(end=pd.Timestamp.now(), periods=30, freq="1D")
    
    # Generar datos aleatorios de volatilidad para diferentes timeframes
    volatility = pd.DataFrame({
        "date": dates,
        "1h": np.random.uniform(1.5, 4.5, size=30),  # Volatilidad de 1 hora
        "4h": np.random.uniform(3, 7, size=30),       # Volatilidad de 4 horas
        "1d": np.random.uniform(5, 12, size=30),      # Volatilidad diaria
    })
    
    # Simular tendencias y patrones
    # Hacer que la volatilidad aumente gradualmente en el tiempo
    volatility["1h"] = volatility["1h"] * np.linspace(0.8, 1.2, 30)
    volatility["4h"] = volatility["4h"] * np.linspace(0.9, 1.1, 30)
    volatility["1d"] = volatility["1d"] * np.linspace(1.0, 1.05, 30)
    
    # Calcular una media móvil de volatilidad para la línea de tendencia
    volatility["1h_sma"] = volatility["1h"].rolling(window=7).mean().fillna(volatility["1h"])
    volatility["4h_sma"] = volatility["4h"].rolling(window=7).mean().fillna(volatility["4h"])
    volatility["1d_sma"] = volatility["1d"].rolling(window=7).mean().fillna(volatility["1d"])
    
    # Colores para el tema
    if theme == "dark":
        bg_color = "#131722"
        grid_color = "#1e222d"
        text_color = "#CCCCCC"
        title_color = "#EEEEEE"
    else:
        bg_color = "#FFFFFF"
        grid_color = "#EEEEEE"
        text_color = "#444444"
        title_color = "#222222"
    
    # Seleccionar los datos según el timeframe
    if timeframe in ["5m", "15m", "30m"]:
        y_column = "1h"
        y_sma_column = "1h_sma"
        title_suffix = "- Alta Frecuencia"
    elif timeframe in ["1h", "4h"]:
        y_column = "4h"
        y_sma_column = "4h_sma"
        title_suffix = "- Media Frecuencia"
    else:  # "1d" o cualquier otro
        y_column = "1d"
        y_sma_column = "1d_sma"
        title_suffix = "- Baja Frecuencia"
    
    # Crear figura
    fig = go.Figure()
    
    # Añadir línea de volatilidad
    fig.add_trace(
        go.Scatter(
            x=volatility["date"], 
            y=volatility[y_column],
            mode="lines",
            name=f"Volatilidad {timeframe}",
            line=dict(width=1, color="#2962FF"),
            fill="tozeroy", 
            fillcolor="rgba(41, 98, 255, 0.2)"
        )
    )
    
    # Añadir línea de tendencia (SMA)
    fig.add_trace(
        go.Scatter(
            x=volatility["date"],
            y=volatility[y_sma_column],
            mode="lines",
            name="Tendencia",
            line=dict(width=2, color="#FF6D00", dash="dash")
        )
    )
    
    # Añadir anotaciones para puntos de volatilidad extrema
    max_vol_idx = volatility[y_column].idxmax()
    min_vol_idx = volatility[y_column].idxmin()
    
    fig.add_annotation(
        x=volatility.iloc[max_vol_idx]["date"],
        y=volatility.iloc[max_vol_idx][y_column],
        text="Volatilidad Max",
        showarrow=True,
        arrowhead=2,
        arrowcolor="#FF3B30",
        arrowsize=1,
        arrowwidth=1,
        ax=0,
        ay=-40,
        font=dict(color="#FF3B30")
    )
    
    fig.add_annotation(
        x=volatility.iloc[min_vol_idx]["date"],
        y=volatility.iloc[min_vol_idx][y_column],
        text="Volatilidad Min",
        showarrow=True,
        arrowhead=2,
        arrowcolor="#34C759",
        arrowsize=1,
        arrowwidth=1,
        ax=0,
        ay=40,
        font=dict(color="#34C759")
    )
    
    # Actualizar layout
    fig.update_layout(
        title={
            "text": f"Análisis de Volatilidad - {pair} {title_suffix}",
            "font": {"color": title_color}
        },
        xaxis={
            "title": "Fecha",
            "gridcolor": grid_color,
            "zerolinecolor": grid_color,
            "tickfont": {"color": text_color},
            "title_font": {"color": text_color}
        },
        yaxis={
            "title": "Volatilidad (%)",
            "gridcolor": grid_color,
            "zerolinecolor": grid_color,
            "tickfont": {"color": text_color},
            "title_font": {"color": text_color}
        },
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        hovermode="x unified",
        legend={"font": {"color": text_color}},
        template="plotly_dark" if theme == "dark" else "plotly_white",
        margin=dict(l=10, r=10, t=50, b=10),
    )
    
    return fig

def create_advanced_analysis_chart(asset="BTC/USDT", timeframe="1h", exchange="binance", theme="dark", indicators=None):
    """Crear un gráfico de análisis técnico avanzado con puntos clave, línea de proyección, etc."""
    # Crear la figura base con subplots para precio y volumen
    fig = create_empty_chart("técnico avanzado", theme)
    
    try:
        # Intentar obtener datos históricos (en un entorno real se usaría get_historical_data)
        # Simulamos datos para propósitos de desarrollo
        np.random.seed(42)
        dates = pd.date_range(end=pd.Timestamp.now(), periods=100, freq=timeframe)
        close = 100 * (1 + np.cumsum(np.random.normal(0, 0.02, size=100)))
        high = close * (1 + np.random.uniform(0, 0.03, size=100))
        low = close * (1 - np.random.uniform(0, 0.03, size=100))
        open_price = close[0] + np.random.normal(0, 0.02, size=100) * close
        volume = np.random.normal(1000000, 500000, size=100)
        
        # Crear DataFrame para facilitar el manejo de datos
        df = pd.DataFrame({
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        }, index=dates)
        
        # Añadir velas al gráfico principal (primera fila de subplots)
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name=asset,
                increasing_line_color='rgb(38, 166, 154)',
                decreasing_line_color='rgb(239, 83, 80)'
            ),
            row=1, col=1
        )
        
        # Añadir volumen (segunda fila de subplots)
        colors = ['rgba(38, 166, 154, 0.7)' if c >= o else 'rgba(239, 83, 80, 0.7)' 
                 for c, o in zip(df['close'], df['open'])]
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['volume'],
                name='Volumen',
                marker_color=colors
            ),
            row=2, col=1
        )
        
        # -------- Añadir puntos clave y líneas de análisis --------
        
        # 1. Niveles de soporte y resistencia (líneas horizontales)
        support_level = df['low'].min() * 1.01
        resistance_level = df['high'].max() * 0.99
        middle_level = (support_level + resistance_level) / 2
        
        # Nivel de soporte (verde)
        fig.add_shape(
            type="line",
            x0=df.index[0],
            y0=support_level,
            x1=df.index[-1],
            y1=support_level,
            line=dict(color="rgba(0, 255, 0, 0.7)", width=1, dash="solid"),
            row=1, col=1
        )
        # Resistencia (roja)
        fig.add_shape(
            type="line",
            x0=df.index[0],
            y0=resistance_level,
            x1=df.index[-1],
            y1=resistance_level,
            line=dict(color="rgba(255, 0, 0, 0.7)", width=1, dash="solid"),
            row=1, col=1
        )
        # Nivel medio (amarillo)
        fig.add_shape(
            type="line",
            x0=df.index[0],
            y0=middle_level,
            x1=df.index[-1],
            y1=middle_level,
            line=dict(color="rgba(255, 255, 0, 0.5)", width=1, dash="dash"),
            row=1, col=1
        )
        
        # 2. Línea de proyección (azul discontinua)
        last_point = df.index[-1]
        future_date = last_point + pd.Timedelta(hours=24)  # Proyección a 24h
        projection_price = df['close'].iloc[-1] * 1.05  # Proyección con 5% de subida
        
        fig.add_shape(
            type="line",
            x0=df.index[-10],  # Comenzar 10 puntos antes del final
            y0=df['close'].iloc[-10],
            x1=future_date,
            y1=projection_price,
            line=dict(color="rgba(0, 100, 255, 0.8)", width=2, dash="dash"),
            row=1, col=1
        )
        
        # 3. Puntos clave de cambio de tendencia (CHoCH, BOS, OB como en las imágenes)
        # Simular algunos puntos importantes
        key_points = [
            {"index": 20, "price": df['high'].iloc[20], "type": "CHoCH", "color": "yellow"},
            {"index": 40, "price": df['low'].iloc[40], "type": "OB", "color": "green"},
            {"index": 60, "price": df['high'].iloc[60], "type": "BOS", "color": "red"},
            {"index": 80, "price": df['low'].iloc[80], "type": "CHoCH", "color": "yellow"}
        ]
        
        for point in key_points:
            # Añadir marcador para el punto
            fig.add_trace(
                go.Scatter(
                    x=[df.index[point["index"]]],
                    y=[point["price"]],
                    mode="markers+text",
                    marker=dict(size=10, color=point["color"], symbol="circle"),
                    text=[point["type"]],
                    textposition="top center",
                    name=point["type"]
                ),
                row=1, col=1
            )
        
        # 4. Niveles de Fibonacci (como en las imágenes)
        # Calcular rango para los niveles
        price_range = resistance_level - support_level
        fib_levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]
        fib_prices = [support_level + level * price_range for level in fib_levels]
        
        for i, (level, price) in enumerate(zip(fib_levels, fib_prices)):
            # Añadir línea para cada nivel Fibonacci
            fig.add_shape(
                type="line",
                x0=df.index[0],
                y0=price,
                x1=df.index[-1],
                y1=price,
                line=dict(color="rgba(255, 255, 255, 0.4)", width=1, dash="dot"),
                row=1, col=1
            )
            
            # Añadir etiqueta
            fig.add_annotation(
                x=df.index[0],
                y=price,
                text=f"Fib {level}",
                showarrow=False,
                xanchor="left",
                font=dict(size=10, color="rgba(255, 255, 255, 0.7)"),
                row=1, col=1
            )
        
        # Actualizar títulos con información del activo
        fig.update_layout(
            title=f"Análisis Técnico Avanzado: {asset} ({timeframe}) - {exchange.capitalize()}"
        )
        
        # Mostrar último precio
        last_price = df['close'].iloc[-1]
        fig.add_annotation(
            x=df.index[-1],
            y=last_price,
            text=f"${last_price:.2f}",
            showarrow=False,
            font=dict(size=14, color="white"),
            bgcolor="rgba(0,0,0,0.7)",
            bordercolor="#c7c7c7",
            borderwidth=1,
            borderpad=4,
            row=1, col=1
        )
    
    except Exception as e:
        # En caso de error, mostrar gráfico vacío con mensaje
        fig.update_layout(
            title=f"Error al cargar datos: {str(e)}"
        )
    
    return fig

def update_analysis_charts(n_clicks, asset, period):
    """Actualiza los gráficos de análisis técnico y volatilidad"""
    if n_clicks is None:
        # Devolver gráficos vacíos si no se ha hecho clic
        return create_empty_chart("técnico"), create_empty_chart("volatilidad")
    
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

def update_volatility_chart(vol_clicks, tf_5m, tf_15m, tf_30m, tf_1h, tf_4h, tf_1d, pair):
    ctx = dash.callback_context
    if not ctx.triggered:
        return create_volatility_chart()
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # Determinar timeframe seleccionado
    timeframe = "1h"  # Valor predeterminado
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
    
    # Simular carga de datos
    time.sleep(0.2) 
    
    # Generar y devolver el gráfico de volatilidad
    return create_volatility_chart(timeframe=timeframe, pair=pair)

def generate_ai_analysis_content(timeframe="1h", pair="BTC/USDT"):
    """Generar contenido de análisis utilizando IA (simulado)"""
    # En un entorno de producción, aquí se integraría con Gemini u otra IA
    # Para el ejemplo, usamos texto estático de análisis
    
    asset_name = pair.split('/')[0]
    price_data = {
        "BTC": {"price": "44,250.25", "resistance": "45,000.00", "support": "38,500.00", "target": "48,500.00"},
        "ETH": {"price": "2,670.35", "resistance": "2,704.88", "support": "2,640.48", "target": "2,580.25"},
        "SOL": {"price": "146.52", "resistance": "160.00", "support": "140.00", "target": "180.00"},
        "XRP": {"price": "0.5125", "resistance": "0.55", "support": "0.50", "target": "0.60"},
        "BNB": {"price": "570.45", "resistance": "600.00", "support": "550.00", "target": "640.00"},
    }
    
    # Usar datos preconfigurados o valores por defecto si el activo no está en la lista
    asset_data = price_data.get(asset_name, {
        "price": "100.00", 
        "resistance": "105.00", 
        "support": "95.00", 
        "target": "110.00"
    })
    
    # Simular diversos escenarios de análisis basados en el par
    if asset_name == "BTC":
        analysis = f"""Análisis de {asset_name} para el timeframe de {timeframe}:

1. Tendencia: Alcista con resistencia en los $45,000. La media móvil de 50 días ha cruzado por encima de la media móvil de 200 días, lo que históricamente ha sido una señal alcista fuerte.

2. Volumen: Ha aumentado significativamente en las últimas sesiones, lo que confirma el interés comprador.

3. Sentimiento: Positivo según análisis de redes sociales y noticias.

4. Riesgos: Regulación gubernamental en mercados importantes puede crear volatilidad a corto plazo.

5. Recomendación: Mantener posición con stop loss en $38,500. Considerar añadir en retrocesos hacia $40,000."""
        color = "success"
    
    elif asset_name == "ETH":
        analysis = f"""Análisis de {asset_name} para el timeframe de {timeframe}:

1. Tendencia: Consolidación lateral después de romper resistencia de $2,200.

2. Factores técnicos: RSI en zona neutral (55), sin señales claras de sobrecompra.

3. Observaciones fundamentales: La actualización EIP-3675 podría ser catalizador positivo en próximos meses.

4. Correlación: Moviéndose más independientemente de BTC en comparación con períodos anteriores.

5. Recomendación: Posición neutral, esperar confirmación de ruptura de $2,600 para entrar largo."""
        color = "info"
        
    else:
        analysis = f"""Análisis de {asset_name} para el timeframe de {timeframe}:

1. Tendencia: {asset_name} muestra una estructura de precio en desarrollo con soporte en ${asset_data['support']} y resistencia en ${asset_data['resistance']}..

2. Volumen: Volumen mixto sin clara dirección dominante.

3. Indicadores técnicos: RSI en rango medio (45-55) indicando neutralidad.

4. Sentimiento: Neutral con ligero sesgo alcista.

5. Recomendación: Esperar confirmación en próximos movimientos de precio para posicionamiento."""
        color = "secondary"
    
    # Generar el contenido HTML para mostrar el análisis
    content = dbc.Card(
        [
            dbc.CardHeader(
                [
                    html.H5(f"Análisis IA para {pair}", className="text-light mb-0 d-inline"),
                    html.Button(
                        html.I(className="fas fa-times"),
                        id="close-analysis-panel",
                        className="btn-close btn-close-white float-end",
                        style={"background": "none"}
                    )
                ],
                className=f"bg-{color}"
            ),
            dbc.CardBody(
                [
                    html.Div(
                        dcc.Markdown(analysis, className="text-light"),
                        className="analysis-text mb-4 overflow-auto", 
                        style={"maxHeight": "400px"}
                    ),
                    
                    html.Hr(className="border-secondary"),
                    
                    html.H6("Key Points", className="text-info mb-2"),
                    html.Ul(
                        [
                            html.Li(
                                ["Precio actual: ", html.Span(f"${asset_data['price']}", className="text-info")],
                                className="small text-light"
                            ),
                            html.Li(
                                ["Resistencia: ", html.Span(f"${asset_data['resistance']}", className="text-danger")],
                                className="small text-light"
                            ),
                            html.Li(
                                ["Soporte: ", html.Span(f"${asset_data['support']}", className="text-success")],
                                className="small text-light"
                            ),
                            html.Li(
                                ["Objetivo: ", html.Span(f"${asset_data['target']}", className="text-warning")], 
                                className="small text-light"
                            ),
                        ],
                        className="ps-3 mb-3"
                    ),
                    
                    html.Hr(className="border-secondary"),
                    
                    html.H6("Escenario Alternativo", className="text-warning mb-2"),
                    html.P(
                        f"Si el precio rompe la resistencia en ${asset_data['resistance']} con volumen alto, podría tener un impulso hacia ${float(asset_data['resistance'].replace(',',''))*1.05:.2f}",
                        className="text-light small mb-3"
                    ),
                    
                    html.Hr(className="border-secondary"),
                    
                    html.H6("SETUP DE TRADING", className="text-danger mb-2"),
                    html.P(
                        f"Para el timeframe {timeframe}: Considerar una estrategia de breakout con entrada en ${asset_data['resistance']} y stop loss en ${asset_data['support']}",
                        className="text-light small mb-2"
                    ),
                ],
            )
        ],
        className="p-3"
    )
    
    return content

# Layout principal de la página de análisis
layout = html.Div(children=[
    # Barra de navegación superior compacta con estilos mejorados
    dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    html.H3("TradingRoad", className="m-0 text-info fw-bold"),
                    href="/",
                    style={"textDecoration": "none"}
                ),
                
                # Grupo de botones para seleccionar Exchange compacto
                dbc.ButtonGroup(
                    [
                        dbc.Button(
                            "Bi...", # Botón con texto abreviado para ahorrar espacio
                            id="exchange-selector-dropdown", 
                            color="dark",
                            size="sm",
                            className="border-secondary",
                            outline=True,
                        ),
                        dbc.DropdownMenu(
                            [
                                dbc.DropdownMenuItem("Binance", id="binance-option"),
                                dbc.DropdownMenuItem("Bybit", id="bybit-option"),
                                dbc.DropdownMenuItem("BingX", id="bingx-option"),
                                dbc.DropdownMenuItem("OKX", id="okx-option"),
                                dbc.DropdownMenuItem("KuCoin", id="kucoin-option"),
                                dbc.DropdownMenuItem("Bitget", id="bitget-option"),
                                dbc.DropdownMenuItem("MEXC", id="mexc-option"),
                            ],
                            size="sm",
                            color="dark",
                            align_end=True,
                        ),
                    ],
                    className="me-1",
                ),
                
                # Grupo de botones para seleccionar par de trading compacto
                dbc.ButtonGroup(
                    [
                        dbc.Button(
                            "BTC/USDT",
                            id="pair-display", 
                            color="dark",
                            size="sm",
                            className="border-secondary",
                            outline=True,
                        ),
                        dbc.DropdownMenu(
                            [
                                dbc.DropdownMenuItem("BTC/USDT", id="btc-usdt-pair"),
                                dbc.DropdownMenuItem("ETH/USDT", id="eth-usdt-pair"),
                                dbc.DropdownMenuItem("BNB/USDT", id="bnb-usdt-pair"),
                                dbc.DropdownMenuItem("SOL/USDT", id="sol-usdt-pair"),
                                dbc.DropdownMenuItem("XRP/USDT", id="xrp-usdt-pair"),
                                dbc.DropdownMenuItem("ADA/USDT", id="ada-usdt-pair"),
                                dbc.DropdownMenuItem("AVAX/USDT", id="avax-usdt-pair"),
                                dbc.DropdownMenuItem("DOT/USDT", id="dot-usdt-pair"),
                            ],
                            size="sm",
                            color="dark",
                            align_end=True,
                        ),
                    ],
                    className="me-1",
                ),
                
                # Grupo de botones para timeframe compacto
                dbc.ButtonGroup(
                    [
                        dbc.Button("5m", id="tf-5m", color="dark", size="sm", className="px-1", outline=True),
                        dbc.Button("15m", id="tf-15m", color="dark", size="sm", className="px-1", outline=True),
                        dbc.Button("30m", id="tf-30m", color="dark", size="sm", className="px-1", outline=True),
                        dbc.Button("1h", id="tf-1h", color="dark", size="sm", className="px-1", outline=True),
                        dbc.Button("4h", id="tf-4h", color="dark", size="sm", className="px-1", outline=True),
                        dbc.Button("1d", id="tf-1d", color="dark", size="sm", className="px-1", outline=True),
                    ],
                    className="me-1",
                ),
                
                # Botón desplegable de indicadores técnicos
                dbc.DropdownMenu(
                    label="Indicadores",
                    children=[
                        # Cada indicador como un checkbox que se puede configurar
                        dbc.DropdownMenuItem(
                            [
                                dbc.Checkbox(id="sma-20-checkbox", label="SMA 20", value=False, className="me-2"),
                                dbc.Input(id="sma-20-value", type="number", value=20, size="sm", style={"width": "60px", "display": "inline-block"}, placeholder="Periodo")
                            ],
                            header="Medias Móviles",
                        ),
                        dbc.DropdownMenuItem(
                            [
                                dbc.Checkbox(id="sma-50-checkbox", label="SMA 50", value=False, className="me-2"),
                                dbc.Input(id="sma-50-value", type="number", value=50, size="sm", style={"width": "60px", "display": "inline-block"}, placeholder="Periodo")
                            ],
                        ),
                        dbc.DropdownMenuItem(
                            [
                                dbc.Checkbox(id="sma-200-checkbox", label="SMA 200", value=False, className="me-2"),
                                dbc.Input(id="sma-200-value", type="number", value=200, size="sm", style={"width": "60px", "display": "inline-block"}, placeholder="Periodo")
                            ],
                        ),
                        dbc.DropdownMenuItem(
                            [
                                dbc.Checkbox(id="ema-20-checkbox", label="EMA 20", value=False, className="me-2"),
                                dbc.Input(id="ema-20-value", type="number", value=20, size="sm", style={"width": "60px", "display": "inline-block"}, placeholder="Periodo")
                            ],
                        ),
                        dbc.DropdownMenuItem(divider=True),
                        dbc.DropdownMenuItem(
                            [
                                dbc.Checkbox(id="rsi-checkbox", label="RSI", value=False, className="me-2"),
                                dbc.Input(id="rsi-value", type="number", value=14, size="sm", style={"width": "60px", "display": "inline-block"}, placeholder="Periodo")
                            ],
                            header="Osciladores",
                        ),
                        dbc.DropdownMenuItem(
                            [
                                dbc.Checkbox(id="macd-checkbox", label="MACD", value=False, className="me-2"),
                            ],
                        ),
                        dbc.DropdownMenuItem(
                            [
                                dbc.Checkbox(id="bollinger-checkbox", label="Bollinger Bands", value=False, className="me-2"),
                                dbc.Input(id="bollinger-value", type="number", value=20, size="sm", style={"width": "60px", "display": "inline-block"}, placeholder="Periodo")
                            ],
                            header="Bandas",
                        ),
                    ],
                    color="dark",
                    size="sm",
                    align_end=True,
                    className="me-1",
                ),
                
                # Botón para cargar datos
                dbc.Button(
                    [
                        html.I(className='fas fa-chart-line me-1'),
                        "Cargar",
                    ],
                    id='load-data-button',
                    color='primary',
                    size='sm',
                    n_clicks=0,
                    className="me-1",
                ),
                
                # Spacer para alinear a la derecha
                html.Div(className="ms-auto d-flex")
            ],
            fluid=True,
        ),
        color="dark",
        dark=True,
        className="mb-2",
    ),
    
    # Fila de botones de control adicionales, más compactos
    dbc.Row([
        dbc.Col([
            dbc.ButtonGroup([
                # Botón para mostrar/ocultar panel de volatilidad
                dbc.Button(
                    html.I(className="fas fa-chart-line"),
                    id="toggle-volatility",
                    color="light",
                    outline=True,
                    size="sm",
                    className="me-1",
                    title="Mostrar/ocultar gráfico de volatilidad"
                ),
                # Botón para mostrar/ocultar panel de correlación
                dbc.Button(
                    html.I(className="fas fa-project-diagram"),
                    id="toggle-correlation",
                    color="light",
                    outline=True,
                    size="sm",
                    className="me-1",
                    title="Mostrar/ocultar correlación de activos"
                ),
                # Botón para mostrar/ocultar panel de análisis AI
                dbc.Button(
                    html.I(className="fas fa-robot"),
                    id="show-ai-button",
                    color="light",
                    outline=True,
                    size="sm",
                    className="me-1",
                    title="Mostrar/ocultar análisis AI"
                ),
                # Botón para cambiar tema claro/oscuro
                dbc.Button(
                    html.I(className="fas fa-sun"),
                    id="theme-toggle",
                    color="light",
                    outline=True,
                    size="sm",
                    className="me-1",
                    title="Cambiar tema claro/oscuro"
                ),
                # Botón para mostrar noticias
                dbc.Button(
                    html.I(className="fas fa-newspaper"),
                    id="news-button",
                    color="light",
                    outline=True,
                    size="sm",
                    className="me-1",
                    title="Ver noticias"
                ),
                # Botón para actualizar en tiempo real
                dbc.Button(
                    dbc.Switch(
                        id="real-time-update",
                        label="Tiempo Real",
                        value=False,
                        className="ms-1"
                    ),
                    color="light",
                    outline=True,
                    size="sm",
                    className="me-1",
                    disabled=True
                ),
            ]),
        ], width="auto"),
    ], className="mb-2 ms-2"),
    
    # Contenedor principal para el gráfico y paneles laterales
    html.Div(
        [
            # Panel lateral de análisis (flotante a la izquierda)
            html.Div(
                [
                    # Cabecera del panel
                    html.Div(
                        [
                            html.H5("AI Analysis Results", className="m-0 text-light"),
                            html.Button(
                                html.I(className="fas fa-times"),
                                id="close-analysis-panel",
                                className="btn-close btn-close-white",
                                style={"background": "none"}
                            ),
                        ],
                        className="d-flex justify-content-between align-items-center p-2 border-bottom border-secondary",
                        style={"backgroundColor": "#1a1a2e"}
                    ),
                    
                    # Contenido del panel con scroll
                    html.Div(
                        id="analysis-ai-content",
                        children=[
                            html.Div(
                                [
                                    html.H6("Primary Scenario", className="text-info mb-2"),
                                    html.P(
                                        "El precio se encuentra en un retroceso bajista desde el ATH y FIB. Es probable que continúe la presión vendedora hasta los niveles de soporte clave en $25xx-2540, donde hay confirmación de demanda en TF menor.",
                                        className="text-light small mb-3"
                                    ),
                                    
                                    html.Div(
                                        [
                                            html.P(
                                                [html.Span("Setup Type: ", className="text-secondary"), "Reversal"],
                                                className="mb-2 small"
                                            ),
                                            html.P(
                                                [html.Span("Direction: ", className="text-secondary"), "Bearish Short-term"],
                                                className="mb-2 small"
                                            ),
                                            html.P(
                                                [html.Span("Key Levels: ", className="text-secondary")],
                                                className="mb-1 small"
                                            ),
                                            html.Ul(
                                                [
                                                    html.Li("Resistance: $2704.88", className="small text-danger"),
                                                    html.Li("Support: $2640.48", className="small text-success"),
                                                    html.Li("Target: $2580.25", className="small"),
                                                ],
                                                className="ps-3 mb-3"
                                            )
                                        ],
                                        className="mb-3 ps-2 border-start border-info"
                                    ),
                                    
                                    html.H6("Alternative Scenario", className="text-warning mb-2"),
                                    html.P(
                                        "Si se rompe el nivel de resistencia en $2704 con confirmación de impulso (volumen creciente), podría dirigirse hacia $2750-2780.",
                                        className="text-light small mb-3"
                                    ),
                                    
                                    html.Hr(className="border-secondary"),
                                    
                                    html.H6("CORTO", className="text-danger mb-2"),
                                    html.P(
                                        "Esta es entrada actual: Buscar una entrada en corto en la zona de oferta $2670-2700, con confirmación de vela de rechazo o ChoCh bajista en 15M. Una entrada agresiva podría ser el retest del nivel BH.",
                                        className="text-light small mb-2"
                                    ),
                                ],
                                className="p-3"
                            )
                        ],
                        style={
                            "maxHeight": "calc(100vh - 200px)",
                            "overflowY": "auto",
                            "backgroundColor": "#131722"
                        },
                    ),
                ],
                id="analysis-panel",
                style={
                    "position": "fixed",
                    "left": "0",
                    "top": "60px",
                    "bottom": "0",
                    "width": "350px",
                    "zIndex": "1000",
                    "backgroundColor": "#131722",
                    "borderRight": "1px solid #2a2e39",
                    "boxShadow": "2px 0 5px rgba(0,0,0,0.2)",
                    "display": "none"  # Inicialmente oculto
                }
            ),
            
            # Contenedor principal para el gráfico - ocupa casi toda la pantalla
            html.Div(
                [
                    # Fila para el gráfico principal 
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Graph(
                                    id="trading-chart",
                                    figure=create_advanced_analysis_chart(), 
                                    style={
                                        "height": "calc(100vh - 130px)",  # Altura dinámica
                                        "backgroundColor": "#131722"
                                    },
                                    config={
                                        "scrollZoom": True,
                                        "displayModeBar": True,
                                        "modeBarButtonsToAdd": [
                                            "drawline",
                                            "drawopenpath",
                                            "drawcircle",
                                            "drawrect",
                                            "eraseshape"
                                        ]
                                    }
                                ),
                                width=12,
                                className="p-0"
                            ),
                        ],
                        className="g-0"
                    ),
                ],
                id="main-chart-container",
                style={
                    "marginLeft": "0px",  # Se actualizará con JavaScript cuando el panel esté visible
                    "transition": "margin-left 0.3s"
                }
            ),
            
            # Panel para gráfico de volatilidad (oculto inicialmente)
            html.Div(
                [
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                [
                                    html.H5("Análisis de Volatilidad", className="text-light mb-0 d-inline"),
                                    html.Button(
                                        html.I(className="fas fa-times"),
                                        id="close-volatility",
                                        className="btn-close btn-close-white float-end",
                                        style={"background": "none"}
                                    ),
                                ],
                                className="d-flex justify-content-between align-items-center",
                                style={"backgroundColor": "#1a1a2e"}
                            ),
                            dbc.CardBody(
                                dcc.Loading(
                                    id="loading-volatility",
                                    children=[
                                        dcc.Graph(
                                            id="volatility-chart",
                                            figure=create_empty_chart("volatilidad"),
                                            style={"height": "300px"}
                                        )
                                    ],
                                )
                            ),
                        ],
                        className="mt-3",
                        style={"backgroundColor": "#131722", "border": "1px solid #2a2e39"}
                    )
                ],
                id="volatility-panel",
                style={"display": "none"}
            ),
            
            # Panel para gráfico de correlación (oculto inicialmente)
            html.Div(
                [
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                [
                                    html.H5("Correlación entre Activos", className="text-light mb-0 d-inline"),
                                    html.Button(
                                        html.I(className="fas fa-times"),
                                        id="close-correlation",
                                        className="btn-close btn-close-white float-end",
                                        style={"background": "none"}
                                    ),
                                ],
                                className="d-flex justify-content-between align-items-center",
                                style={"backgroundColor": "#1a1a2e"}
                            ),
                            dbc.CardBody(
                                dcc.Loading(
                                    id="loading-correlation",
                                    children=[
                                        dcc.Graph(
                                            id="correlation-chart",
                                            figure=create_correlation_heatmap(),
                                            style={"height": "400px"}
                                        )
                                    ],
                                )
                            ),
                        ],
                        className="mt-3",
                        style={"backgroundColor": "#131722", "border": "1px solid #2a2e39"}
                    )
                ],
                id="correlation-panel",
                style={"display": "none"}
            ),
        ],
        style={"position": "relative"}
    ),
    
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
    ]),
    
    # Modal para noticias
    dbc.Modal(
        [
            dbc.ModalHeader("Noticias Recientes", close_button=True),
            dbc.ModalBody(
                [
                    dbc.Spinner(
                        id="news-loading-spinner",
                        children=[
                            html.Div(
                                id="news-content",
                                children=[
                                    # Ejemplo de noticias predefinidas
                                    dbc.ListGroup(
                                        [
                                            dbc.ListGroupItem(
                                                [
                                                    html.Div(
                                                        [
                                                            html.H5("Bitcoin supera los $65,000 tras aprobación del ETF", className="mb-1"),
                                                            html.Small("Publicado hace 2 horas", className="text-muted"),
                                                        ],
                                                        className="d-flex w-100 justify-content-between"
                                                    ),
                                                    html.P(
                                                        "El precio de Bitcoin ha superado los $65,000 tras la aprobación del primer ETF de Bitcoin al contado en Estados Unidos...",
                                                        className="mb-1"
                                                    ),
                                                    html.Small("Fuente: CoinDesk"),
                                                ],
                                                action=True,
                                            ),
                                            dbc.ListGroupItem(
                                                [
                                                    html.Div(
                                                        [
                                                            html.H5("Ethereum completa actualización a PoS", className="mb-1"),
                                                            html.Small("Publicado hace 1 día", className="text-muted"),
                                                        ],
                                                        className="d-flex w-100 justify-content-between"
                                                    ),
                                                    html.P(
                                                        "Ethereum ha completado con éxito su transición a Proof of Stake, reduciendo su consumo energético en un 99.95%...",
                                                        className="mb-1"
                                                    ),
                                                    html.Small("Fuente: Ethereum Foundation"),
                                                ],
                                                action=True,
                                            ),
                                            dbc.ListGroupItem(
                                                [
                                                    html.Div(
                                                        [
                                                            html.H5("Regulación cripto avanza en Europa con MiCA", className="mb-1"),
                                                            html.Small("Publicado hace 3 días", className="text-muted"),
                                                        ],
                                                        className="d-flex w-100 justify-content-between"
                                                    ),
                                                    html.P(
                                                        "El Parlamento Europeo ha aprobado la regulación MiCA, estableciendo un marco regulatorio completo para criptoactivos en la UE...",
                                                        className="mb-1"
                                                    ),
                                                    html.Small("Fuente: European Commission"),
                                                ],
                                                action=True,
                                            ),
                                        ]
                                    )
                                ]
                            )
                        ],
                    )
                ]
            ),
        ],
        id="news-modal",
        size="lg",
    ),
    
    # Componente de intervalo para actualizaciones automáticas
    dcc.Interval(
        id='chart-interval',
        interval=15*1000,  # 15 segundos
        n_intervals=0,
        disabled=True
    ),
])

# La función generate_ai_analysis_content ya está implementada anteriormente en el archivo
# en las líneas 603-737, por lo que eliminamos esta versión duplicada.
