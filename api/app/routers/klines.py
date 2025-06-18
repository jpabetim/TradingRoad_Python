"""
Router para datos OHLCV (Klines)
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import pandas as pd
from datetime import datetime

# Importar utilidades
from app.utils.market_data import MarketDataClient

router = APIRouter()

@router.get("/klines", response_model=Dict[str, Any])
async def get_klines(
    symbol: str = Query(..., description="Par de trading (ej: BTC/USDT)"),
    interval: str = Query("1h", description="Intervalo de tiempo (ej: 1m, 5m, 15m, 1h, 4h, 1d)"),
    limit: int = Query(100, description="Cantidad de velas a retornar", ge=1, le=1000),
    exchange: str = Query("binance", description="ID del exchange"),
    since: Optional[int] = Query(None, description="Timestamp UNIX en milisegundos para inicio de datos")
):
    """
    Obtiene datos OHLCV (Open, High, Low, Close, Volume) para un par de trading específico.
    Este es el endpoint principal para alimentar los gráficos de velas en el frontend.
    """
    try:
        client = MarketDataClient(exchange_id=exchange)
        df = client.get_ohlcv_data(symbol, interval, limit, since)
        
        if df.empty:
            raise HTTPException(
                status_code=404, 
                detail=f"No hay datos disponibles para {symbol} en {exchange} con intervalo {interval}"
            )
        
        # Convertir el DataFrame a formato compatible con Lightweight Charts
        result = {
            "symbol": symbol,
            "interval": interval,
            "exchange": exchange,
            "lastUpdate": datetime.now().isoformat(),
            "data": []
        }
        
        # Formato para Lightweight Charts con objetos individuales por vela
        for _, row in df.iterrows():
            result["data"].append({
                "time": row["timestamp"].value // 10**6,  # Convertir a milisegundos
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row["volume"])
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo datos: {str(e)}")


@router.get("/klines/export", response_model=Dict[str, Any])
async def export_klines(
    symbol: str = Query(..., description="Par de trading (ej: BTC/USDT)"),
    interval: str = Query("1h", description="Intervalo de tiempo (ej: 1m, 5m, 15m, 1h, 4h, 1d)"),
    limit: int = Query(100, description="Cantidad de velas a retornar", ge=1, le=1000),
    exchange: str = Query("binance", description="ID del exchange"),
    format: str = Query("csv", description="Formato de exportación (csv, json)")
):
    """
    Exporta datos OHLCV en formato CSV o JSON para descarga
    """
    try:
        client = MarketDataClient(exchange_id=exchange)
        df = client.get_ohlcv_data(symbol, interval, limit)
        
        if df.empty:
            raise HTTPException(
                status_code=404, 
                detail=f"No hay datos disponibles para {symbol} en {exchange} con intervalo {interval}"
            )
            
        if format.lower() == "csv":
            csv_data = df.to_csv(index=False)
            return {
                "format": "csv",
                "symbol": symbol,
                "interval": interval,
                "exchange": exchange,
                "data": csv_data
            }
        else:
            # Formato JSON estándar
            json_data = df.to_json(orient="records", date_format="iso")
            return {
                "format": "json",
                "symbol": symbol,
                "interval": interval, 
                "exchange": exchange,
                "data": json_data
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exportando datos: {str(e)}")
