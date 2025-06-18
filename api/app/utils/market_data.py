"""
Módulo de utilidades para obtener datos de mercados en tiempo real
exclusivamente a través de CCXT para mayor compatibilidad y robustez
"""

import os
import time
import json
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
import ccxt

class MarketDataClient:
    """Cliente para obtener datos de mercado exclusivamente a través de CCXT"""
    
    def __init__(self, exchange_id="binance", api_key=None, api_secret=None):
        # Manejo de casos donde se pasa un diccionario de configuración completo
        if isinstance(exchange_id, dict):
            config = exchange_id
            # Intentar extraer exchange_id del diccionario de configuración
            if "exchange" in config:
                self.exchange_id = config["exchange"].lower()
            elif "default_exchange" in config:
                self.exchange_id = config["default_exchange"].lower()
            else:
                self.exchange_id = "binance"  # Valor predeterminado
            
            # Intentar extraer API keys si están presentes en el config
            try:
                if self.exchange_id in config:
                    self.api_key = config[self.exchange_id].get('api_key')
                    self.api_secret = config[self.exchange_id].get('api_secret')
                elif 'ccxt' in config and 'exchanges' in config['ccxt'] and \
                     self.exchange_id in config['ccxt']['exchanges']:
                    exchange_config = config['ccxt']['exchanges'][self.exchange_id]
                    self.api_key = exchange_config.get('api_key')
                    self.api_secret = exchange_config.get('api_secret')
                    self.api_password = exchange_config.get('password')
            except Exception as e:
                print(f"Error al extraer configuración del diccionario: {e}")
        else:
            # Manejo normal cuando se pasa un string
            self.exchange_id = str(exchange_id).lower()
            self.api_key = api_key
            self.api_secret = api_secret
            
        self.ccxt_client = None
        
        # Intentar cargar configuración desde archivo si existe
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'exchanges.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    exchanges_config = json.load(f)
                    
                    # Buscar configuración en formato antiguo
                    if self.exchange_id in exchanges_config and not api_key and not api_secret:
                        self.api_key = exchanges_config[self.exchange_id].get('api_key')
                        self.api_secret = exchanges_config[self.exchange_id].get('api_secret')
                    # Buscar configuración en formato nuevo (ccxt.exchanges)
                    elif 'ccxt' in exchanges_config and 'exchanges' in exchanges_config['ccxt'] and \
                         self.exchange_id in exchanges_config['ccxt']['exchanges']:
                        exchange_config = exchanges_config['ccxt']['exchanges'][self.exchange_id]
                        self.api_key = exchange_config.get('api_key')
                        self.api_secret = exchange_config.get('api_secret')
                        self.api_password = exchange_config.get('password')  # Algunos exchanges requieren password
        except Exception as e:
            print(f"Error al cargar configuración de exchanges: {e}")
        
        # Inicializar cliente CCXT
        self._init_ccxt_client()
    
    def _init_ccxt_client(self):
        """Inicializar el cliente CCXT para el exchange configurado"""
        if self.exchange_id in ccxt.exchanges:
            try:
                exchange_class = getattr(ccxt, self.exchange_id)
                
                # Asegurar que api_key y api_secret estén inicializados
                if not hasattr(self, 'api_key') or self.api_key is None:
                    self.api_key = ""
                if not hasattr(self, 'api_secret') or self.api_secret is None:
                    self.api_secret = ""
                
                config = {
                    'apiKey': self.api_key,
                    'secret': self.api_secret,
                    'enableRateLimit': True,
                    'timeout': 30000,
                }
                
                # Añadir password si existe (necesario para algunos exchanges como KuCoin)
                if hasattr(self, 'api_password') and self.api_password:
                    config['password'] = self.api_password
                    
                self.ccxt_client = exchange_class(config)
                print(f"Cliente CCXT para {self.exchange_id} inicializado correctamente")
            except Exception as e:
                print(f"Error al inicializar cliente CCXT para {self.exchange_id}: {e}")
                self._fallback_to_binance()
        else:
            print(f"Error: Exchange {self.exchange_id} no soportado por CCXT")
            self._fallback_to_binance()
    
    def _fallback_to_binance(self):
        """Usar Binance como fallback si el exchange solicitado no está disponible"""
        self.exchange_id = "binance"  # Fallback a Binance
        self.ccxt_client = ccxt.binance({
            'apiKey': None,
            'secret': None,
            'enableRateLimit': True,
            'timeout': 30000,
        })
        print(f"Cliente CCXT para {self.exchange_id} (fallback) inicializado correctamente")
    
    def _timeframe_to_interval(self, timeframe):
        """Convertir formato de timeframe al formato estándar de CCXT"""
        # CCXT usa un formato estándar para timeframes que la mayoría de exchanges soportan
        standard_timeframes = {
            '1m': '1m', '3m': '3m', '5m': '5m', '15m': '15m', '30m': '30m',
            '1h': '1h', '2h': '2h', '4h': '4h', '6h': '6h', '8h': '8h', '12h': '12h',
            '1d': '1d', '3d': '3d', '1w': '1w', '1M': '1M'
        }
        
        # Si el timeframe ya está en formato estándar CCXT
        if timeframe in standard_timeframes:
            return timeframe
        
        # Intentar hacer algunas conversiones comunes
        conversions = {
            '1': '1m', '5': '5m', '15': '15m', '30': '30m',
            '60': '1h', '120': '2h', '240': '4h',
            '1440': '1d', '10080': '1w', '43200': '1M'
        }
        
        if timeframe in conversions:
            return conversions[timeframe]
            
        # Si no se puede convertir, devolver el timeframe original
        # (CCXT intentará adaptarlo según el exchange)
        return timeframe
        
    def get_ohlcv_data(self, symbol, timeframe='1h', limit=100, since=None):
        """Obtener datos OHLCV a través de CCXT"""
        try:
            # Asegurarse de que tenemos un cliente CCXT válido
            if not self.ccxt_client:
                self._init_ccxt_client()
                
            # Verificar si el exchange soporta OHLCV
            if not self.ccxt_client.has['fetchOHLCV']:
                print(f"Exchange {self.exchange_id} no soporta OHLCV")
                return self.generate_mock_data(symbol, timeframe, limit)
            
            # Convertir timeframe al formato estándar de CCXT
            tf = self._timeframe_to_interval(timeframe)
            
            # Obtener datos OHLCV
            ohlcv = self.ccxt_client.fetch_ohlcv(symbol, tf, limit=limit, since=since)
            
            # Verificar si se obtuvieron datos
            if not ohlcv or len(ohlcv) == 0:
                print(f"No se obtuvieron datos para {symbol} en {self.exchange_id}")
                return self.generate_mock_data(symbol, timeframe, limit)
            
            # Convertir a DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Asegurar que está ordenado por timestamp
            df = df.sort_values('timestamp')
            
            return df
                
        except Exception as e:
            print(f"Error al obtener datos de {self.exchange_id} via CCXT: {str(e)}")
            return self.generate_mock_data(symbol, timeframe, limit)
    
    def generate_mock_data(self, symbol, timeframe='1h', limit=100):
        """Generar datos simulados para pruebas y fallback"""
        # Mapeo de timeframe a minutos para simulación
        timeframe_minutes = {
            '1m': 1, '5m': 5, '15m': 15, '30m': 30,
            '1h': 60, '2h': 120, '4h': 240, '6h': 360, '8h': 480, '12h': 720,
            '1d': 1440, '3d': 4320, '1w': 10080, '1M': 43200
        }
        
        minutes = timeframe_minutes.get(self._timeframe_to_interval(timeframe), 60)
        end_time = datetime.now()
        
        # Generar timestamps
        times = [end_time - timedelta(minutes=minutes * i) for i in range(limit)]
        times.reverse()
        
        # Base inicial basada en el activo
        base_asset = symbol.split('/')[0] if '/' in symbol else 'UNKNOWN'
        
        if base_asset == 'BTC':
            base_price = 65000
            volatility = 1200
        elif base_asset == 'ETH':
            base_price = 3200
            volatility = 180
        elif base_asset == 'BNB':
            base_price = 570
            volatility = 15
        elif base_asset == 'SOL':
            base_price = 146
            volatility = 8
        elif base_asset == 'XRP':
            base_price = 0.50
            volatility = 0.03
        elif base_asset == 'ADA':
            base_price = 0.45
            volatility = 0.025
        else:
            base_price = 100
            volatility = 5
            
        # Generar precios simulando una tendencia realista
        np.random.seed(int(time.time()) % 100)  # Usar tiempo actual para seed diferente cada vez
        price_changes = np.random.randn(limit) * (volatility * 0.01)
        # Añadir un pequeño componente de tendencia
        trend = np.linspace(-0.01, 0.01, limit) * base_price
        price_changes = price_changes + trend
        
        close_prices = base_price + np.cumsum(price_changes)
        open_prices = close_prices - np.random.randn(limit) * (volatility * 0.005)
        high_prices = np.maximum(close_prices, open_prices) + np.abs(np.random.randn(limit) * (volatility * 0.008))
        low_prices = np.minimum(close_prices, open_prices) - np.abs(np.random.randn(limit) * (volatility * 0.008))
        
        # Generar volumen realista correlacionado con la volatilidad
        base_volume = base_price * 10  # Mayor precio, mayor volumen base
        volatility_factor = np.abs(price_changes) / np.mean(np.abs(price_changes))
        volumes = base_volume * (0.5 + volatility_factor)
        
        # Crear DataFrame
        df = pd.DataFrame({
            'timestamp': times,
            'open': open_prices,
            'high': high_prices,
            'low': low_prices,
            'close': close_prices,
            'volume': volumes
        })
        
        print(f"Generando datos simulados para {symbol} - {timeframe}")
        return df
    
    def get_available_exchanges(self):
        """Obtener lista de exchanges disponibles en CCXT"""
        # Devolver los exchanges más populares primero, luego el resto
        popular_exchanges = ['binance', 'bybit', 'kucoin', 'okx', 'coinbase', 'kraken', 'bitget', 'mexc']
        other_exchanges = [ex for ex in ccxt.exchanges if ex not in popular_exchanges]
        return popular_exchanges + other_exchanges
    
    def get_available_pairs(self, exchange=None):
        """Obtener pares disponibles para el exchange actual o uno específico"""
        try:
            # Si se especifica un exchange diferente, creamos un cliente temporal
            if exchange and exchange != self.exchange_id:
                temp_client = MarketDataClient(exchange_id=exchange)
                return temp_client.get_available_pairs()
            
            # Usamos el cliente actual
            if self.ccxt_client:
                # Cargar mercados si no están cargados
                if not hasattr(self.ccxt_client, 'markets') or not self.ccxt_client.markets:
                    self.ccxt_client.load_markets()
                
                # Filtrar solo pares activos con USDT, BUSD o USDC
                pairs = []
                for symbol, market in self.ccxt_client.markets.items():
                    if market['active'] and ('/USDT' in symbol or '/BUSD' in symbol or '/USDC' in symbol):
                        pairs.append(symbol)
                
                if pairs:
                    return sorted(pairs)
            
            # Fallback a pares predeterminados
            return self._get_default_pairs()
                
        except Exception as e:
            print(f"Error al obtener pares para {self.exchange_id}: {str(e)}")
            return self._get_default_pairs()
    
    def _get_default_pairs(self):
        """Lista predeterminada de pares comunes"""
        return [
            'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 
            'ADA/USDT', 'XRP/USDT', 'DOT/USDT', 'AVAX/USDT',
            'DOGE/USDT', 'SHIB/USDT', 'MATIC/USDT', 'LTC/USDT'
        ]
        
    # Método de compatibilidad con código antiguo
    def get_market_data(self, exchange, symbol, timeframe='1h', limit=100):
        """Obtener datos de mercado (compatibilidad con código antiguo)"""
        # Si se especifica un exchange diferente del actual, crear un cliente temporal
        if exchange != self.exchange_id:
            temp_client = MarketDataClient(exchange_id=exchange)
            return temp_client.get_ohlcv_data(symbol, timeframe, limit)
        
        # Usar el cliente actual
        return self.get_ohlcv_data(symbol, timeframe, limit)


# Funciones auxiliares para uso directo sin necesidad de instanciar la clase
def get_ohlcv_data(exchange="binance", symbol="BTC/USDT", timeframe="1h", limit=100, since=None):
    """
    Obtiene datos OHLCV para un símbolo y timeframe específicos
    Esta función es un wrapper sobre MarketDataClient.get_ohlcv_data para facilitar su uso
    
    Args:
        exchange (str): ID del exchange (por defecto 'binance')
        symbol (str): Símbolo en formato 'BTC/USDT'
        timeframe (str): Intervalo de tiempo ('1m', '5m', '15m', '1h', '4h', '1d', etc)
        limit (int): Cantidad máxima de velas a obtener
        since (int): Timestamp UNIX en milisegundos para inicio de datos
        
    Returns:
        DataFrame: Datos OHLCV con columnas [timestamp, open, high, low, close, volume]
    """
    client = MarketDataClient(exchange)
    return client.get_ohlcv_data(symbol, timeframe, limit, since)
