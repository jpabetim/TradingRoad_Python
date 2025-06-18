"""
Router para manejo de conexiones WebSocket
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import asyncio

from app.utils.websocket_manager import ConnectionManager, DataBroadcaster

router = APIRouter()

# Inicializar gestor de conexiones
connection_manager = ConnectionManager()
data_broadcaster = DataBroadcaster(connection_manager)

# Iniciar broadcaster al importar el módulo
@router.on_event("startup")
async def startup_broadcaster():
    """Inicia el broadcaster de datos en tiempo real al iniciar la aplicación"""
    await data_broadcaster.start(interval_seconds=5.0)  # Actualizar cada 5 segundos

@router.on_event("shutdown") 
async def shutdown_broadcaster():
    """Detiene el broadcaster de datos al cerrar la aplicación"""
    await data_broadcaster.stop()

@router.websocket("/ws/klines/{symbol}")
async def websocket_klines(
    websocket: WebSocket, 
    symbol: str,
    exchange: Optional[str] = None
):
    """
    Endpoint WebSocket para recibir actualizaciones en tiempo real de un símbolo
    
    El formato del símbolo puede ser simple o compuesto:
    - Simple: "BTC/USDT" (se usa Binance por defecto)
    - Compuesto: "exchange:BTC/USDT" (ej: "binance:BTC/USDT")
    """
    # Procesar símbolo compuesto si es necesario
    full_symbol = symbol
    if exchange and ":" not in symbol:
        full_symbol = f"{exchange}:{symbol}"
    
    # Aceptar la conexión
    await connection_manager.connect(websocket, full_symbol)
    
    try:
        # Mantener la conexión abierta y escuchar mensajes
        while True:
            # Esperar mensaje del cliente
            message = await websocket.receive_text()
            
            # Procesar comandos del cliente (suscripción, desuscripción, etc.)
            try:
                # Si el mensaje es un ping, responder con pong
                if message == "ping":
                    await websocket.send_text("pong")
            except Exception as e:
                # Si hay error procesando el mensaje, enviar error al cliente
                await websocket.send_text(f"Error: {str(e)}")
                
    except WebSocketDisconnect:
        # Cuando el cliente se desconecta, eliminarlo de la lista
        await connection_manager.disconnect(websocket, full_symbol)
        
@router.get("/ws/stats", tags=["websocket"])
async def get_websocket_stats():
    """
    Obtiene estadísticas de conexiones WebSocket activas
    """
    symbols = connection_manager.get_subscribed_symbols()
    stats = {
        "total_connections": connection_manager.get_connections_count(),
        "active_symbols": len(symbols),
        "symbols": {
            symbol: connection_manager.get_connections_count(symbol)
            for symbol in symbols
        }
    }
    return stats
