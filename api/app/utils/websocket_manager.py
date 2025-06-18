"""
Utilidades para gestión de conexiones WebSocket
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Set
from fastapi import WebSocket, WebSocketDisconnect

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    Clase para manejar conexiones WebSocket de clientes
    """
    
    def __init__(self):
        # Diccionario que mapea símbolos a un conjunto de conexiones activas
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Almacena el último mensaje enviado a cada símbolo
        self.last_data: Dict[str, Dict[str, Any]] = {}
        
    async def connect(self, websocket: WebSocket, symbol: str):
        """Acepta conexión WebSocket y la registra para un símbolo"""
        await websocket.accept()
        
        # Inicializar conjunto de conexiones para este símbolo si no existe
        if symbol not in self.active_connections:
            self.active_connections[symbol] = set()
            
        # Agregar esta conexión al conjunto para el símbolo
        self.active_connections[symbol].add(websocket)
        
        # Enviar el último dato conocido para este símbolo, si existe
        if symbol in self.last_data:
            try:
                await websocket.send_text(json.dumps(self.last_data[symbol]))
            except Exception as e:
                logger.error(f"Error enviando datos iniciales: {str(e)}")
                
        # Log de la conexión
        total_connections = sum(len(conns) for conns in self.active_connections.values())
        logger.info(f"Cliente conectado para {symbol}. Total conexiones: {total_connections}")
        
    async def disconnect(self, websocket: WebSocket, symbol: str):
        """Elimina una conexión cuando se desconecta"""
        if symbol in self.active_connections:
            try:
                self.active_connections[symbol].remove(websocket)
                
                # Si no hay más conexiones para este símbolo, limpiar recursos
                if not self.active_connections[symbol]:
                    del self.active_connections[symbol]
                    if symbol in self.last_data:
                        del self.last_data[symbol]
                        
                # Log de la desconexión
                total_connections = sum(len(conns) for conns in self.active_connections.values())
                logger.info(f"Cliente desconectado de {symbol}. Total conexiones: {total_connections}")
            except KeyError:
                pass
        
    async def broadcast(self, symbol: str, data: Dict[str, Any]):
        """Envía datos a todos los clientes conectados a un símbolo específico"""
        if symbol not in self.active_connections:
            return
            
        # Guardar este dato como el último para este símbolo
        self.last_data[symbol] = data
        
        # Preparar el mensaje JSON una sola vez
        message = json.dumps(data)
        
        # Conexiones a eliminar (no podemos modificar el set mientras iteramos)
        disconnected = set()
        
        # Enviar a cada cliente conectado
        for connection in self.active_connections[symbol]:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error enviando datos: {str(e)}")
                disconnected.add(connection)
        
        # Eliminar conexiones muertas
        for connection in disconnected:
            await self.disconnect(connection, symbol)
            
    def get_subscribed_symbols(self) -> List[str]:
        """Devuelve lista de símbolos con suscripciones activas"""
        return list(self.active_connections.keys())
        
    def get_connections_count(self, symbol: str = None) -> int:
        """
        Devuelve el número de conexiones activas
        Si se especifica símbolo, devuelve solo para ese símbolo
        """
        if symbol:
            return len(self.active_connections.get(symbol, set()))
        else:
            return sum(len(conns) for conns in self.active_connections.values())


class DataBroadcaster:
    """
    Clase para gestionar la transmisión periódica de datos
    a través de conexiones WebSocket
    """
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.should_stop = False
        self.task = None
        
    async def start(self, interval_seconds: float = 5.0):
        """Inicia el bucle de transmisión de datos"""
        self.should_stop = False
        self.task = asyncio.create_task(self._broadcast_loop(interval_seconds))
        
    async def stop(self):
        """Detiene el bucle de transmisión de datos"""
        self.should_stop = True
        if self.task:
            await self.task
        
    async def _broadcast_loop(self, interval_seconds: float):
        """Bucle principal que envía datos a intervalos regulares"""
        from app.utils.market_data import MarketDataClient
        
        while not self.should_stop:
            try:
                # Obtener lista de símbolos con suscriptores activos
                symbols = self.connection_manager.get_subscribed_symbols()
                
                # Si no hay símbolos con suscriptores, esperar
                if not symbols:
                    await asyncio.sleep(interval_seconds)
                    continue
                
                # Procesar cada símbolo
                for symbol in symbols:
                    try:
                        # Si no hay conexiones para este símbolo, saltar
                        if self.connection_manager.get_connections_count(symbol) == 0:
                            continue
                            
                        # Obtener últimos datos para este símbolo (por defecto de Binance en 1m)
                        interval = "1m"  # Intervalos más cortos para tiempo real
                        exchange = "binance"  # Por defecto usamos Binance
                        
                        # Extraer símbolo y exchange si están en formato compuesto "binance:BTC/USDT"
                        if ":" in symbol:
                            parts = symbol.split(":")
                            if len(parts) == 2:
                                exchange, symbol_only = parts
                                symbol = symbol_only
                        
                        # Obtener último dato
                        client = MarketDataClient(exchange_id=exchange)
                        df = client.get_ohlcv_data(symbol, interval, limit=1)
                        
                        if not df.empty:
                            # Crear objeto de datos para enviar
                            kline_data = {
                                "type": "kline_update",
                                "symbol": symbol,
                                "exchange": exchange,
                                "interval": interval,
                                "timestamp": int(time.time() * 1000),
                                "data": {
                                    "time": df["timestamp"].iloc[0].value // 10**6,  # ms
                                    "open": float(df["open"].iloc[0]),
                                    "high": float(df["high"].iloc[0]),
                                    "low": float(df["low"].iloc[0]),
                                    "close": float(df["close"].iloc[0]),
                                    "volume": float(df["volume"].iloc[0])
                                }
                            }
                            
                            # Broadcast a todos los clientes de este símbolo
                            await self.connection_manager.broadcast(symbol, kline_data)
                    
                    except Exception as e:
                        logger.error(f"Error procesando símbolo {symbol}: {str(e)}")
                
                # Esperar antes de la siguiente iteración
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error en bucle de broadcast: {str(e)}")
                # Si hay un error, esperar antes de reintentar
                await asyncio.sleep(interval_seconds)
