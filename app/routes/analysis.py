from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import google.generativeai as genai

from app import models, schemas
from app.core import deps
from app.config import settings

router = APIRouter()

# Configurar Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

@router.get("/market-data/{symbol}")
async def get_market_data(
    symbol: str,
    timeframe: str = "1h",
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Obtener datos de mercado para un símbolo específico
    """
    try:
        # Aquí normalmente obtendríamos los datos de un exchange
        # Para este ejemplo, generamos datos sintéticos
        end_date = datetime.now()
        
        # Determinar el intervalo en segundos según el timeframe
        if timeframe == "1m":
            interval = 60
        elif timeframe == "5m":
            interval = 300
        elif timeframe == "15m":
            interval = 900
        elif timeframe == "30m":
            interval = 1800
        elif timeframe == "1h":
            interval = 3600
        elif timeframe == "4h":
            interval = 14400
        elif timeframe == "1d":
            interval = 86400
        else:
            interval = 3600  # default: 1h
            
        start_date = end_date - timedelta(seconds=interval * limit)
        
        # Generar fechas para el período
        dates = pd.date_range(
            start=start_date, 
            end=end_date, 
            periods=limit
        )
        
        # Generar datos sintéticos para el gráfico de velas
        np.random.seed(42)
        close_price = 100 + np.cumsum(np.random.randn(limit) * 2)
        open_price = close_price - np.random.randn(limit) * 1.5
        high_price = np.maximum(close_price, open_price) + np.random.rand(limit) * 3
        low_price = np.minimum(close_price, open_price) - np.random.rand(limit) * 3
        volume = np.random.rand(limit) * 100
        
        # Crear los datos en formato OHLCV
        data = []
        for i in range(limit):
            data.append({
                "timestamp": dates[i].isoformat(),
                "open": float(open_price[i]),
                "high": float(high_price[i]),
                "low": float(low_price[i]),
                "close": float(close_price[i]),
                "volume": float(volume[i])
            })
            
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "data": data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener datos de mercado: {str(e)}",
        )

@router.get("/indicators/{symbol}")
async def calculate_indicators(
    symbol: str,
    timeframe: str = "1h",
    indicators: List[str] = ["sma", "ema", "rsi"],
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Calcular indicadores técnicos para un símbolo
    """
    try:
        # Primero obtenemos los datos de mercado
        market_data_response = await get_market_data(symbol, timeframe, limit, db, current_user)
        market_data = market_data_response["data"]
        
        # Convertir datos a un DataFrame de pandas para facilitar el cálculo de indicadores
        df = pd.DataFrame(market_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        result = {
            "symbol": symbol,
            "timeframe": timeframe,
            "indicators": {}
        }
        
        # Calcular los indicadores solicitados
        for indicator in indicators:
            if indicator == "sma":
                # Media Móvil Simple (20 períodos)
                sma_20 = df['close'].rolling(window=20).mean()
                result["indicators"]["sma_20"] = [
                    {"timestamp": ts.isoformat(), "value": float(val) if not pd.isna(val) else None} 
                    for ts, val in zip(df['timestamp'], sma_20)
                ]
                
                # Media Móvil Simple (50 períodos)
                sma_50 = df['close'].rolling(window=50).mean()
                result["indicators"]["sma_50"] = [
                    {"timestamp": ts.isoformat(), "value": float(val) if not pd.isna(val) else None} 
                    for ts, val in zip(df['timestamp'], sma_50)
                ]
                
                # Media Móvil Simple (200 períodos)
                sma_200 = df['close'].rolling(window=200).mean()
                result["indicators"]["sma_200"] = [
                    {"timestamp": ts.isoformat(), "value": float(val) if not pd.isna(val) else None} 
                    for ts, val in zip(df['timestamp'], sma_200)
                ]
                
            elif indicator == "ema":
                # Media Móvil Exponencial (20 períodos)
                ema_20 = df['close'].ewm(span=20, adjust=False).mean()
                result["indicators"]["ema_20"] = [
                    {"timestamp": ts.isoformat(), "value": float(val)} 
                    for ts, val in zip(df['timestamp'], ema_20)
                ]
                
                # Media Móvil Exponencial (50 períodos)
                ema_50 = df['close'].ewm(span=50, adjust=False).mean()
                result["indicators"]["ema_50"] = [
                    {"timestamp": ts.isoformat(), "value": float(val)} 
                    for ts, val in zip(df['timestamp'], ema_50)
                ]
                
            elif indicator == "rsi":
                # RSI (14 períodos)
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                result["indicators"]["rsi_14"] = [
                    {"timestamp": ts.isoformat(), "value": float(val) if not pd.isna(val) else None} 
                    for ts, val in zip(df['timestamp'], rsi)
                ]
                
            elif indicator == "bollinger":
                # Bandas de Bollinger (20 períodos, 2 desviaciones estándar)
                sma_20 = df['close'].rolling(window=20).mean()
                std_20 = df['close'].rolling(window=20).std()
                upper_band = sma_20 + 2 * std_20
                lower_band = sma_20 - 2 * std_20
                
                result["indicators"]["bollinger_upper"] = [
                    {"timestamp": ts.isoformat(), "value": float(val) if not pd.isna(val) else None} 
                    for ts, val in zip(df['timestamp'], upper_band)
                ]
                result["indicators"]["bollinger_middle"] = [
                    {"timestamp": ts.isoformat(), "value": float(val) if not pd.isna(val) else None} 
                    for ts, val in zip(df['timestamp'], sma_20)
                ]
                result["indicators"]["bollinger_lower"] = [
                    {"timestamp": ts.isoformat(), "value": float(val) if not pd.isna(val) else None} 
                    for ts, val in zip(df['timestamp'], lower_band)
                ]
                
            elif indicator == "macd":
                # MACD (12, 26, 9)
                ema_12 = df['close'].ewm(span=12, adjust=False).mean()
                ema_26 = df['close'].ewm(span=26, adjust=False).mean()
                macd_line = ema_12 - ema_26
                signal_line = macd_line.ewm(span=9, adjust=False).mean()
                histogram = macd_line - signal_line
                
                result["indicators"]["macd_line"] = [
                    {"timestamp": ts.isoformat(), "value": float(val)} 
                    for ts, val in zip(df['timestamp'], macd_line)
                ]
                result["indicators"]["macd_signal"] = [
                    {"timestamp": ts.isoformat(), "value": float(val)} 
                    for ts, val in zip(df['timestamp'], signal_line)
                ]
                result["indicators"]["macd_histogram"] = [
                    {"timestamp": ts.isoformat(), "value": float(val)} 
                    for ts, val in zip(df['timestamp'], histogram)
                ]
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular indicadores: {str(e)}",
        )

@router.post("/ai-analysis")
async def generate_ai_analysis(
    symbol: str,
    timeframe: str,
    period: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Generar análisis con IA utilizando Gemini
    """
    try:
        # Verificar si el usuario tiene el nivel adecuado para usar análisis de IA
        if current_user.user_level not in ["premium", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Necesitas una cuenta Premium para usar el análisis de IA"
            )
        
        # Iniciar análisis en segundo plano
        # En una implementación real, esto se ejecutaría como una tarea en segundo plano
        # y el resultado se almacenaría en la base de datos
        
        prompt = f"""
        Realiza un análisis técnico y fundamental del activo {symbol} para el periodo de {period} en el timeframe {timeframe}.
        Estructura el análisis en los siguientes puntos:
        
        1. Tendencia actual
        2. Soportes y resistencias clave
        3. Indicadores técnicos destacados (RSI, MACD, Medias Móviles)
        4. Factores fundamentales relevantes
        5. Posibles escenarios a corto plazo
        6. Recomendación general
        
        Proporciona datos específicos y rangos de precios cuando sea posible.
        """
        
        # Llamar a la API de Gemini
        response = model.generate_content(prompt)
        
        # Procesar respuesta
        analysis_text = response.text
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "period": period,
            "analysis": analysis_text,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar análisis con IA: {str(e)}",
        )
