from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
import os
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import json
import random
from typing import Optional

from app.config import settings
from app.utils.trading_utils import get_candle_data

# Set up templates
templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "templates")
templates = Jinja2Templates(directory=templates_dir)

# Create router
router = APIRouter()

@router.get("/analysis/tradingview", tags=["trading"])
async def tradingview_charts(request: Request):
    """
    Muestra la página de análisis con gráficos de TradingView Lightweight Charts.
    """
    return templates.TemplateResponse("trading_chart.html", {"request": request})

@router.get("/api/v1/market/candles", tags=["api", "market"])
async def get_market_candles(
    symbol: str = "ETHUSDT",
    timeframe: str = "5m",
    exchange: str = "binance_futures",
    limit: int = 100
):
    """
    Obtiene datos de velas (OHLCV) para un par de trading específico.
    
    Args:
        symbol: Par de trading (ej. ETHUSDT)
        timeframe: Marco temporal (ej. 5m, 1h, 4h, 1d)
        exchange: Exchange de donde obtener los datos
        limit: Cantidad de velas a devolver
        
    Returns:
        Lista de velas en formato OHLCV
    """
    try:
        # Intentar obtener datos reales del exchange a través de la función existente
        data = get_candle_data(symbol, timeframe, exchange, limit)
        
        if data is not None and not data.empty:
            # Formato para TradingView Lightweight Charts
            result = []
            for _, row in data.iterrows():
                result.append({
                    "time": row["timestamp"].strftime("%Y-%m-%d"),
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": float(row["volume"])
                })
            return result
    except Exception as e:
        print(f"Error obteniendo datos reales: {str(e)}")
    
    # Si no se pueden obtener datos reales, generar datos de ejemplo
    return generate_sample_data(limit, symbol)

def generate_sample_data(days=100, symbol="ETHUSDT"):
    """
    Genera datos simulados de OHLCV para pruebas.
    
    Args:
        days: Cantidad de velas a generar
        symbol: Símbolo para determinar el rango de precios
    
    Returns:
        Lista de diccionarios con datos OHLCV
    """
    # Determinar precio base según el símbolo
    if "BTC" in symbol:
        starting_price = 35000 + random.uniform(-2000, 2000)
        volatility = 1.5
    elif "ETH" in symbol:
        starting_price = 2500 + random.uniform(-200, 200)
        volatility = 2.0
    else:
        starting_price = 100 + random.uniform(-10, 10)
        volatility = 3.0
    
    # Configurar tendencia aleatoria
    trend = random.uniform(-0.2, 0.2)
    
    # Generar fechas
    dates = [(datetime.now() - timedelta(days=days-i)).strftime('%Y-%m-%d') for i in range(days)]
    
    # Inicializar precios
    opens = [starting_price]
    highs = []
    lows = []
    closes = []
    volumes = []
    
    # Generar datos OHLCV
    for i in range(1, days):
        open_price = opens[-1]
        change = np.random.normal(trend, volatility) * open_price / 100
        close = open_price + change
        high = max(open_price, close) + abs(np.random.normal(0, volatility/2) * open_price / 100)
        low = min(open_price, close) - abs(np.random.normal(0, volatility/2) * open_price / 100)
        
        opens.append(close)  # El siguiente open es el close anterior
        highs.append(high)
        lows.append(low)
        closes.append(close)
        
        # Volumen correlacionado con el cambio de precio
        volume = abs(change) * random.uniform(8000, 15000) / volatility
        volumes.append(volume)
    
    # Ajustar para el primer día
    highs.insert(0, opens[0] + abs(np.random.normal(0, volatility/2) * opens[0] / 100))
    lows.insert(0, opens[0] - abs(np.random.normal(0, volatility/2) * opens[0] / 100))
    closes.insert(0, opens[0] + np.random.normal(trend, volatility) * opens[0] / 100)
    volumes.insert(0, random.uniform(8000, 15000))
    
    # Crear lista de diccionarios
    result = []
    for i in range(days):
        result.append({
            "time": dates[i],
            "open": round(opens[i], 2),
            "high": round(highs[i], 2),
            "low": round(lows[i], 2),
            "close": round(closes[i], 2),
            "volume": round(volumes[i], 2)
        })
    
    return result
