"""
Utilidades para análisis técnico de mercados financieros
"""
import pandas as pd
import numpy as np

def generate_analysis(df, symbol, timeframe):
    """
    Genera un análisis técnico completo en formato HTML basado en datos OHLCV
    
    Args:
        df: DataFrame con datos OHLCV
        symbol: Símbolo del activo
        timeframe: Temporalidad de los datos
        
    Returns:
        str: HTML con el análisis técnico completo
    """
    if df.empty:
        return f"""
        <div style="padding: 15px; margin-bottom: 20px; border-left: 4px solid #FF5555; background-color: rgba(255, 85, 85, 0.1);">
            <h3 style="color: #FF5555;">Sin datos disponibles</h3>
            <p>No hay datos disponibles para {symbol} en temporalidad {timeframe}.</p>
        </div>
        """
    
    # Calculamos los principales indicadores técnicos
    try:
        # Precios actuales
        current_price = df['close'].iloc[-1]
        prev_price = df['close'].iloc[-2] if len(df) > 1 else current_price
        price_change = ((current_price - prev_price) / prev_price) * 100
        price_change_str = f"{price_change:.2f}%"
        price_change_color = "#4CAF50" if price_change >= 0 else "#F44336"
        
        # Medias móviles
        if len(df) >= 20:
            df['sma_20'] = df['close'].rolling(window=20).mean()
            current_sma_20 = df['sma_20'].iloc[-1]
            sma_signal = "Alcista" if current_price > current_sma_20 else "Bajista"
            sma_signal_color = "#4CAF50" if sma_signal == "Alcista" else "#F44336"
        else:
            sma_signal = "Sin datos suficientes"
            sma_signal_color = "#9E9E9E"
            current_sma_20 = None
        
        # RSI
        if len(df) >= 14:
            delta = df['close'].diff()
            gain = delta.where(delta > 0, 0).rolling(window=14).mean()
            loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            current_rsi = df['rsi'].iloc[-1]
            
            if current_rsi > 70:
                rsi_signal = "Sobrecompra"
                rsi_signal_color = "#F44336"
            elif current_rsi < 30:
                rsi_signal = "Sobreventa"
                rsi_signal_color = "#4CAF50"
            else:
                rsi_signal = "Neutral"
                rsi_signal_color = "#9E9E9E"
        else:
            rsi_signal = "Sin datos suficientes"
            rsi_signal_color = "#9E9E9E"
            current_rsi = None
        
        # Soportes y resistencias simples (últimos máximos y mínimos)
        last_n = min(20, len(df))
        recent_highs = df['high'].iloc[-last_n:].nlargest(3)
        recent_lows = df['low'].iloc[-last_n:].nsmallest(3)
        
        resistance_1 = round(recent_highs.iloc[0], 2)
        resistance_2 = round(recent_highs.iloc[1], 2) if len(recent_highs) > 1 else None
        
        support_1 = round(recent_lows.iloc[0], 2)
        support_2 = round(recent_lows.iloc[1], 2) if len(recent_lows) > 1 else None
        
        # Determinación de tendencia
        if current_sma_20 and len(df) >= 50:
            df['sma_50'] = df['close'].rolling(window=50).mean()
            current_sma_50 = df['sma_50'].iloc[-1]
            
            if current_price > current_sma_20 > current_sma_50:
                trend = "Fuertemente alcista"
                trend_color = "#4CAF50"
            elif current_price > current_sma_20:
                trend = "Alcista"
                trend_color = "#8BC34A"
            elif current_price < current_sma_50 < current_sma_20:
                trend = "Fuertemente bajista"
                trend_color = "#F44336"
            elif current_price < current_sma_20:
                trend = "Bajista"
                trend_color = "#FF9800"
            else:
                trend = "Neutral"
                trend_color = "#9E9E9E"
        else:
            if current_sma_20 and current_price > current_sma_20:
                trend = "Alcista"
                trend_color = "#4CAF50"
            elif current_sma_20:
                trend = "Bajista"
                trend_color = "#F44336"
            else:
                trend = "Sin datos suficientes"
                trend_color = "#9E9E9E"
        
        # Generar HTML para el análisis
        analysis_html = f"""
        <div style="font-family: Arial, sans-serif; padding: 15px; margin-bottom: 20px; background-color: rgba(30, 30, 30, 0.7); border-radius: 5px;">
            <h3 style="color: #1E90FF; border-bottom: 1px solid #333; padding-bottom: 10px;">Análisis Técnico: {symbol} ({timeframe})</h3>
            
            <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                <div style="flex: 1; margin-right: 10px; background-color: rgba(40, 40, 40, 0.7); padding: 10px; border-radius: 5px;">
                    <h4 style="color: #ddd; margin-top: 0;">Precio Actual</h4>
                    <p style="font-size: 1.2em; font-weight: bold;">${current_price:,.2f} <span style="color: {price_change_color};">{price_change_str}</span></p>
                </div>
                <div style="flex: 1; margin-left: 10px; background-color: rgba(40, 40, 40, 0.7); padding: 10px; border-radius: 5px;">
                    <h4 style="color: #ddd; margin-top: 0;">Tendencia</h4>
                    <p style="font-size: 1.2em; font-weight: bold; color: {trend_color};">{trend}</p>
                </div>
            </div>
            
            <div style="margin-top: 15px; background-color: rgba(40, 40, 40, 0.7); padding: 10px; border-radius: 5px;">
                <h4 style="color: #ddd; margin-top: 0;">Soportes y Resistencias</h4>
                <div style="display: flex; justify-content: space-between;">
                    <div>
                        <p><strong>Soporte 1:</strong> <span style="color: #4CAF50;">${support_1:,.2f}</span></p>
                        {f'<p><strong>Soporte 2:</strong> <span style="color: #8BC34A;">${support_2:,.2f}</span></p>' if support_2 else ''}
                    </div>
                    <div>
                        <p><strong>Resistencia 1:</strong> <span style="color: #F44336;">${resistance_1:,.2f}</span></p>
                        {f'<p><strong>Resistencia 2:</strong> <span style="color: #FF9800;">${resistance_2:,.2f}</span></p>' if resistance_2 else ''}
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 15px; background-color: rgba(40, 40, 40, 0.7); padding: 10px; border-radius: 5px;">
                <h4 style="color: #ddd; margin-top: 0;">Indicadores</h4>
                <p><strong>SMA (20):</strong> {f"${current_sma_20:.2f} - <span style='color: {sma_signal_color}'>{sma_signal}</span>" if current_sma_20 else "Sin datos suficientes"}</p>
                <p><strong>RSI (14):</strong> {f"{current_rsi:.1f} - <span style='color: {rsi_signal_color}'>{rsi_signal}</span>" if current_rsi else "Sin datos suficientes"}</p>
            </div>
        </div>
        """
        
        return analysis_html
    
    except Exception as e:
        # En caso de error en el cálculo de indicadores
        return f"""
        <div style="padding: 15px; margin-bottom: 20px; border-left: 4px solid #FF9800; background-color: rgba(255, 152, 0, 0.1);">
            <h3 style="color: #FF9800;">Análisis Parcial</h3>
            <p>Se encontraron problemas al calcular algunos indicadores técnicos para {symbol} ({timeframe}).</p>
            <p>Error: {str(e)}</p>
            <p>Precio actual: ${df['close'].iloc[-1]:,.2f}</p>
        </div>
        """


def calculate_volatility(df, window=14):
    """
    Calcula la volatilidad de un activo basada en la desviación estándar de los rendimientos
    
    Args:
        df: DataFrame con datos OHLCV
        window: Ventana de tiempo para el cálculo (por defecto 14 períodos)
        
    Returns:
        float: Valor de volatilidad anualizada (en porcentaje)
    """
    if df.empty or len(df) < window:
        return 0.0
    
    # Calcular rendimientos logarítmicos diarios
    returns = np.log(df["close"] / df["close"].shift(1))
    
    # Calcular desviación estándar de los rendimientos
    std_dev = returns.rolling(window=window).std().iloc[-1]
    
    # Anualizar la volatilidad (dependiendo del timeframe)
    # Por simplicidad asumimos timeframe diario
    annualized_vol = std_dev * np.sqrt(252) * 100  # 252 días de trading al año
    
    return annualized_vol


def get_technical_indicators(df, window_short=20, window_medium=50, window_long=200, rsi_period=14):
    """
    Calcula indicadores técnicos principales para un DataFrame OHLCV
    
    Args:
        df: DataFrame con datos OHLCV
        window_short: Ventana corta para SMA (por defecto 20)
        window_medium: Ventana media para SMA (por defecto 50)
        window_long: Ventana larga para SMA (por defecto 200)
        rsi_period: Período para RSI (por defecto 14)
        
    Returns:
        dict: Diccionario con los indicadores calculados
    """
    if df.empty:
        return {}
        
    result = {}
    
    # Medias Móviles
    result["sma_short"] = df["close"].rolling(window=window_short).mean().iloc[-1]
    result["sma_medium"] = df["close"].rolling(window=window_medium).mean().iloc[-1]
    result["sma_long"] = df["close"].rolling(window=window_long).mean().iloc[-1]
    
    # RSI
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0).fillna(0)
    loss = -delta.where(delta < 0, 0).fillna(0)
    
    avg_gain = gain.rolling(window=rsi_period).mean()
    avg_loss = loss.rolling(window=rsi_period).mean()
    
    rs = avg_gain / avg_loss
    result["rsi"] = 100 - (100 / (1 + rs)).iloc[-1]
    
    # MACD
    ema12 = df["close"].ewm(span=12, adjust=False).mean()
    ema26 = df["close"].ewm(span=26, adjust=False).mean()
    result["macd"] = (ema12 - ema26).iloc[-1]
    result["macd_signal"] = (ema12 - ema26).ewm(span=9, adjust=False).mean().iloc[-1]
    
    # Volatilidad
    result["volatility"] = calculate_volatility(df)
    
    # Últimos precios
    result["current_price"] = df["close"].iloc[-1]
    result["prev_close"] = df["close"].iloc[-2] if len(df) > 1 else 0
    
    return result
