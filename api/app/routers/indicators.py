"""
Router para indicadores técnicos
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np

# Importar utilidades
from app.utils.market_data import MarketDataClient
from app.utils.technical_analysis import get_technical_indicators, calculate_volatility

router = APIRouter()

@router.get("/indicators/all", response_model=Dict[str, Any])
async def get_all_indicators(
    symbol: str = Query(..., description="Par de trading (ej: BTC/USDT)"),
    interval: str = Query("1h", description="Intervalo de tiempo (ej: 1m, 5m, 15m, 1h, 4h, 1d)"),
    limit: int = Query(200, description="Cantidad de velas para cálculo", ge=50, le=1000),
    exchange: str = Query("binance", description="ID del exchange")
):
    """
    Obtiene un conjunto completo de indicadores técnicos para un activo
    """
    try:
        client = MarketDataClient(exchange_id=exchange)
        df = client.get_ohlcv_data(symbol, interval, limit)
        
        if df.empty or len(df) < 50:  # Necesitamos al menos 50 velas para cálculos confiables
            raise HTTPException(
                status_code=404, 
                detail=f"Datos insuficientes para {symbol} en {exchange} con intervalo {interval}"
            )
            
        # Obtenemos todos los indicadores
        indicators = get_technical_indicators(df)
        
        # Formateamos para devolver valores precisos
        result = {
            "symbol": symbol,
            "interval": interval,
            "exchange": exchange,
            "price": {
                "current": round(float(indicators["current_price"]), 8),
                "previous": round(float(indicators["prev_close"]), 8),
                "change_pct": round(((indicators["current_price"] / indicators["prev_close"]) - 1) * 100, 2) 
                               if indicators["prev_close"] > 0 else 0
            },
            "moving_averages": {
                "sma20": round(float(indicators["sma_short"]), 8),
                "sma50": round(float(indicators["sma_medium"]), 8),
                "sma200": round(float(indicators["sma_long"]), 8),
                "trend": "bullish" if indicators["current_price"] > indicators["sma_short"] > indicators["sma_medium"] 
                         else "bearish" if indicators["current_price"] < indicators["sma_short"] < indicators["sma_medium"]
                         else "neutral"
            },
            "oscillators": {
                "rsi": round(float(indicators["rsi"]), 2),
                "rsi_signal": "overbought" if indicators["rsi"] > 70 else "oversold" if indicators["rsi"] < 30 else "neutral",
                "macd": round(float(indicators["macd"]), 8),
                "macd_signal": round(float(indicators["macd_signal"]), 8),
                "macd_histogram": round(float(indicators["macd"] - indicators["macd_signal"]), 8)
            },
            "volatility": {
                "value": round(float(indicators["volatility"]), 2),
                "level": "high" if indicators["volatility"] > 50 
                         else "medium" if indicators["volatility"] > 25
                         else "low"
            }
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculando indicadores: {str(e)}")

@router.get("/indicators/sma", response_model=Dict[str, Any])
async def get_sma_data(
    symbol: str = Query(..., description="Par de trading (ej: BTC/USDT)"),
    interval: str = Query("1h", description="Intervalo de tiempo (ej: 1m, 5m, 15m, 1h, 4h, 1d)"),
    periods: List[int] = Query([20, 50, 200], description="Periodos para SMA"),
    limit: int = Query(200, description="Cantidad de velas para cálculo", ge=1, le=1000),
    exchange: str = Query("binance", description="ID del exchange")
):
    """
    Obtiene datos de Medias Móviles Simples (SMA) para los períodos especificados
    """
    try:
        client = MarketDataClient(exchange_id=exchange)
        df = client.get_ohlcv_data(symbol, interval, limit)
        
        if df.empty:
            raise HTTPException(
                status_code=404, 
                detail=f"No hay datos disponibles para {symbol} en {exchange} con intervalo {interval}"
            )
        
        result = {
            "symbol": symbol,
            "interval": interval,
            "exchange": exchange,
            "data": []
        }
        
        # Calcular SMA para cada período
        for period in sorted(periods):
            if len(df) >= period:
                df[f'sma_{period}'] = df['close'].rolling(window=period).mean()
                
                # Crear serie temporal con valores
                series_data = []
                for idx, row in df.iterrows():
                    if not pd.isna(row[f'sma_{period}']):
                        series_data.append({
                            "time": row["timestamp"].value // 10**6,  # Convertir a milisegundos
                            "value": float(row[f'sma_{period}'])
                        })
                
                result["data"].append({
                    "period": period,
                    "series": series_data,
                    "lastValue": float(df[f'sma_{period}'].iloc[-1]) if len(series_data) > 0 else None
                })
                
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculando SMA: {str(e)}")

@router.get("/indicators/rsi", response_model=Dict[str, Any])
async def get_rsi_data(
    symbol: str = Query(..., description="Par de trading (ej: BTC/USDT)"),
    interval: str = Query("1h", description="Intervalo de tiempo (ej: 1m, 5m, 15m, 1h, 4h, 1d)"),
    period: int = Query(14, description="Periodo para RSI"),
    limit: int = Query(200, description="Cantidad de velas para cálculo", ge=20, le=1000),
    exchange: str = Query("binance", description="ID del exchange")
):
    """
    Obtiene datos de RSI (Relative Strength Index)
    """
    try:
        client = MarketDataClient(exchange_id=exchange)
        df = client.get_ohlcv_data(symbol, interval, limit)
        
        if df.empty or len(df) < period + 5:  # Necesitamos suficientes datos
            raise HTTPException(
                status_code=404, 
                detail=f"Datos insuficientes para {symbol} en {exchange} con intervalo {interval}"
            )
        
        # Calcular RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Crear respuesta
        result = {
            "symbol": symbol,
            "interval": interval,
            "exchange": exchange,
            "period": period,
            "currentValue": round(float(df['rsi'].iloc[-1]), 2),
            "signal": "overbought" if df['rsi'].iloc[-1] > 70
                     else "oversold" if df['rsi'].iloc[-1] < 30
                     else "neutral",
            "data": []
        }
        
        # Crear serie temporal de datos
        for idx, row in df.iterrows():
            if not pd.isna(row['rsi']):
                result["data"].append({
                    "time": row["timestamp"].value // 10**6,  # Convertir a milisegundos
                    "value": float(row['rsi'])
                })
                
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculando RSI: {str(e)}")


@router.get("/indicators/bands", response_model=Dict[str, Any])
async def get_bollinger_bands(
    symbol: str = Query(..., description="Par de trading (ej: BTC/USDT)"),
    interval: str = Query("1h", description="Intervalo de tiempo (ej: 1m, 5m, 15m, 1h, 4h, 1d)"),
    period: int = Query(20, description="Período para Bandas de Bollinger"),
    std_dev: float = Query(2.0, description="Desviaciones estándar para las bandas", ge=0.5, le=3.0),
    limit: int = Query(200, description="Cantidad de velas para cálculo", ge=30, le=1000),
    exchange: str = Query("binance", description="ID del exchange")
):
    """
    Obtiene datos de Bandas de Bollinger
    """
    try:
        client = MarketDataClient(exchange_id=exchange)
        df = client.get_ohlcv_data(symbol, interval, limit)
        
        if df.empty or len(df) < period + 5:
            raise HTTPException(
                status_code=404, 
                detail=f"Datos insuficientes para {symbol} en {exchange} con intervalo {interval}"
            )
        
        # Calcular Bandas de Bollinger
        df['sma'] = df['close'].rolling(window=period).mean()
        df['std'] = df['close'].rolling(window=period).std()
        df['upper'] = df['sma'] + (df['std'] * std_dev)
        df['lower'] = df['sma'] - (df['std'] * std_dev)
        
        # Crear respuesta
        result = {
            "symbol": symbol,
            "interval": interval,
            "exchange": exchange,
            "period": period,
            "standardDeviation": std_dev,
            "currentValues": {
                "middle": round(float(df['sma'].iloc[-1]), 8),
                "upper": round(float(df['upper'].iloc[-1]), 8),
                "lower": round(float(df['lower'].iloc[-1]), 8),
                "width": round(float((df['upper'].iloc[-1] - df['lower'].iloc[-1]) / df['sma'].iloc[-1]) * 100, 2)  # Ancho en porcentaje
            },
            "middle": [],
            "upper": [],
            "lower": []
        }
        
        # Crear series temporales para cada banda
        for idx, row in df.iterrows():
            if not pd.isna(row['sma']) and not pd.isna(row['upper']) and not pd.isna(row['lower']):
                time_ms = row["timestamp"].value // 10**6
                
                result["middle"].append({
                    "time": time_ms,
                    "value": float(row['sma'])
                })
                
                result["upper"].append({
                    "time": time_ms,
                    "value": float(row['upper'])
                })
                
                result["lower"].append({
                    "time": time_ms,
                    "value": float(row['lower'])
                })
                
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculando Bandas de Bollinger: {str(e)}")
