"""
Router para información de exchanges y pares disponibles
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any

# Importar utilidades
from app.utils.market_data import MarketDataClient

router = APIRouter()

@router.get("/exchanges", response_model=Dict[str, Any])
async def get_exchanges():
    """
    Obtiene la lista de exchanges disponibles a través de CCXT
    """
    try:
        client = MarketDataClient()
        exchanges = client.get_available_exchanges()
        
        return {
            "count": len(exchanges),
            "exchanges": exchanges
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo exchanges: {str(e)}")

@router.get("/exchanges/{exchange_id}/pairs", response_model=Dict[str, Any])
async def get_exchange_pairs(
    exchange_id: str = Query(..., description="ID del exchange (ej: binance, bybit, etc)")
):
    """
    Obtiene los pares de trading disponibles para un exchange específico
    """
    try:
        client = MarketDataClient(exchange_id=exchange_id)
        pairs = client.get_available_pairs()
        
        # Organizar por tipo de activo
        categorized_pairs = {}
        for pair in pairs:
            base_asset = pair.split('/')[0] if '/' in pair else "OTROS"
            if base_asset not in categorized_pairs:
                categorized_pairs[base_asset] = []
            categorized_pairs[base_asset].append(pair)
        
        return {
            "exchange": exchange_id,
            "count": len(pairs),
            "pairs": pairs,
            "categorized": categorized_pairs
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo pares para {exchange_id}: {str(e)}")

@router.get("/exchanges/{exchange_id}/info", response_model=Dict[str, Any])
async def get_exchange_info(
    exchange_id: str = Query(..., description="ID del exchange (ej: binance, bybit, etc)")
):
    """
    Obtiene información general sobre un exchange específico
    """
    try:
        client = MarketDataClient(exchange_id=exchange_id)
        
        # Verificamos que el exchange exista
        if not client.ccxt_client:
            raise HTTPException(status_code=404, detail=f"Exchange {exchange_id} no encontrado")
        
        # Obtenemos información básica
        exchange_info = {
            "id": exchange_id,
            "name": client.ccxt_client.name if hasattr(client.ccxt_client, 'name') else exchange_id.title(),
            "supported_features": {
                "fetchOHLCV": client.ccxt_client.has.get('fetchOHLCV', False),
                "fetchTicker": client.ccxt_client.has.get('fetchTicker', False),
                "fetchOrderBook": client.ccxt_client.has.get('fetchOrderBook', False)
            }
        }
        
        return exchange_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo información de {exchange_id}: {str(e)}")
