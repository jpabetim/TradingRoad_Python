"""
Módulo de utilidades para obtener datos de mercados en tiempo real
desde diferentes exchanges (Binance, BingX y otros a través de CCXT)
"""

import os
import time
import json
import hmac
import hashlib
import requests
from datetime import datetime, timedelta
import pandas as pd
import ccxt
from urllib.parse import urlencode

# Configuración de exchanges
DEFAULT_BINANCE_API_URL = "https://api.binance.com"
DEFAULT_BINGX_API_URL = "https://open-api.bingx.com"

class MarketDataClient:
    """Cliente para obtener datos de mercado de varios exchanges"""
    
    def __init__(self, config=None):
        """Inicializar cliente con configuración opcional"""
        self.config = config or {}
        self.binance_api_key = self.config.get('binance', {}).get('api_key', '')
        self.binance_api_secret = self.config.get('binance', {}).get('api_secret', '')
        self.bingx_api_key = self.config.get('bingx', {}).get('api_key', '')
        self.bingx_api_secret = self.config.get('bingx', {}).get('api_secret', '')
        
        # Inicializar CCXT para múltiples exchanges
        self.ccxt_exchanges = {}
        
    def init_ccxt_exchange(self, exchange_id):
        """Inicializar un exchange específico en CCXT"""
        if exchange_id in ccxt.exchanges:
            exchange_class = getattr(ccxt, exchange_id)
            exchange_config = self.config.get(exchange_id, {})
            
            self.ccxt_exchanges[exchange_id] = exchange_class({
                'apiKey': exchange_config.get('api_key', ''),
                'secret': exchange_config.get('api_secret', ''),
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
            return True
        return False

    def _timeframe_to_interval(self, timeframe, exchange='binance'):
        """Convertir formato de timeframe a formato específico del exchange"""
        # Mappings específicos por exchange
        mappings = {
            'binance': {
                '5m': '5m', '15m': '15m', '30m': '30m', 
                '1h': '1h', '4h': '4h', '1d': '1d', '1w': '1w'
            },
            'bingx': {
                '5m': '5', '15m': '15', '30m': '30',
                '1h': '60', '4h': '240', '1d': '1440', '1w': '10080'
            }
        }
        
        return mappings.get(exchange, {}).get(timeframe, '1h')
    
    def get_binance_klines(self, symbol, timeframe='1h', limit=100):
        """Obtener datos OHLCV de Binance"""
        try:
            interval = self._timeframe_to_interval(timeframe, 'binance')
            params = {
                'symbol': symbol.replace('/', ''),
                'interval': interval,
                'limit': limit
            }
            
            # Añadir autenticación si hay credenciales
            headers = {}
            if self.binance_api_key:
                headers['X-MBX-APIKEY'] = self.binance_api_key
                
            response = requests.get(
                f"{DEFAULT_BINANCE_API_URL}/api/v3/klines", 
                params=params,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data, columns=[
                    'timestamp', 'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_volume', 'trades', 'taker_buy_base', 
                    'taker_buy_quote', 'ignored'
                ])
                
                # Convertir tipos
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    df[col] = df[col].astype(float)
                    
                return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            else:
                print(f"Error en respuesta Binance: {response.text}")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"Error al obtener datos de Binance: {str(e)}")
            return pd.DataFrame()

    def get_bingx_klines(self, symbol, timeframe='1h', limit=100):
        """Obtener datos OHLCV de BingX"""
        try:
            interval = self._timeframe_to_interval(timeframe, 'bingx')
            
            # BingX utiliza un formato diferente para los símbolos (BTC-USDT en lugar de BTC/USDT)
            bingx_symbol = symbol.replace('/', '-')
            
            # Preparar parámetros
            params = {
                'symbol': bingx_symbol,
                'interval': interval,
                'limit': limit
            }
            
            # Añadir timestamp y firma si hay credenciales
            if self.bingx_api_key and self.bingx_api_secret:
                timestamp = int(time.time() * 1000)
                params['timestamp'] = timestamp
                
                # Crear firma HMAC
                query_string = urlencode(sorted(params.items()))
                signature = hmac.new(
                    self.bingx_api_secret.encode('utf-8'),
                    query_string.encode('utf-8'),
                    hashlib.sha256
                ).hexdigest()
                
                params['signature'] = signature
                headers = {'X-BX-APIKEY': self.bingx_api_key}
            else:
                headers = {}
                
            # Hacer la petición
            response = requests.get(
                f"{DEFAULT_BINGX_API_URL}/openApi/swap/v2/quote/klines", 
                params=params,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if result['code'] == 0 and 'data' in result:
                    data = result['data']
                    df = pd.DataFrame(data, columns=[
                        'timestamp', 'open', 'high', 'low', 'close', 'volume', 
                        'close_time', 'quote_volume', 'trades', 'taker_buy_volume',
                        'taker_buy_quote_volume', 'ignore'
                    ])
                    
                    # Convertir tipos
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    for col in ['open', 'high', 'low', 'close', 'volume']:
                        df[col] = df[col].astype(float)
                        
                    return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
                else:
                    print(f"Error en respuesta BingX: {result}")
                    return pd.DataFrame()
            else:
                print(f"Error en respuesta BingX: {response.text}")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"Error al obtener datos de BingX: {str(e)}")
            return pd.DataFrame()
    
    def get_ccxt_klines(self, exchange_id, symbol, timeframe='1h', limit=100):
        """Obtener datos OHLCV a través de CCXT"""
        try:
            # Inicializar exchange si no está ya inicializado
            if exchange_id not in self.ccxt_exchanges:
                if not self.init_ccxt_exchange(exchange_id):
                    print(f"Exchange {exchange_id} no disponible en CCXT")
                    return pd.DataFrame()
            
            exchange = self.ccxt_exchanges[exchange_id]
            
            # Verificar si el exchange está disponible
            if exchange.has['fetchOHLCV']:
                # Obtener datos OHLCV
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                
                # Convertir a DataFrame
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                
                return df
            else:
                print(f"Exchange {exchange_id} no soporta OHLCV")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"Error al obtener datos de {exchange_id} via CCXT: {str(e)}")
            return pd.DataFrame()
    
    def get_market_data(self, exchange, symbol, timeframe='1h', limit=100):
        """Obtener datos de mercado del exchange especificado"""
        if exchange == 'binance':
            return self.get_binance_klines(symbol, timeframe, limit)
        elif exchange == 'bingx':
            return self.get_bingx_klines(symbol, timeframe, limit)
        elif exchange in ccxt.exchanges:
            return self.get_ccxt_klines(exchange, symbol, timeframe, limit)
        else:
            # Datos simulados como fallback
            print(f"Exchange {exchange} no soportado. Generando datos simulados.")
            return self.generate_mock_data(symbol, timeframe, limit)
    
    def generate_mock_data(self, symbol, timeframe='1h', limit=100):
        """Generar datos simulados para pruebas"""
        import numpy as np
        
        # Mapeo de timeframe a minutos
        timeframe_minutes = {
            '5m': 5, '15m': 15, '30m': 30,
            '1h': 60, '4h': 240, '1d': 1440, '1w': 10080
        }
        
        minutes = timeframe_minutes.get(timeframe, 60)
        end_time = datetime.now()
        
        # Generar timestamps
        times = [end_time - timedelta(minutes=minutes * i) for i in range(limit)]
        times.reverse()
        
        # Base inicial basada en el activo
        if 'BTC' in symbol:
            base_price = 65000
            volatility = 1200
        elif 'ETH' in symbol:
            base_price = 3200
            volatility = 180
        else:
            base_price = 100
            volatility = 5
            
        # Generar precios con volatilidad adecuada
        np.random.seed(42)
        price_changes = np.random.randn(limit) * (volatility * 0.01)
        close_prices = base_price + np.cumsum(price_changes)
        open_prices = close_prices - np.random.randn(limit) * (volatility * 0.005)
        high_prices = np.maximum(close_prices, open_prices) + np.abs(np.random.randn(limit) * (volatility * 0.008))
        low_prices = np.minimum(close_prices, open_prices) - np.abs(np.random.randn(limit) * (volatility * 0.008))
        volumes = np.random.rand(limit) * 100
        
        # Crear DataFrame
        df = pd.DataFrame({
            'timestamp': times,
            'open': open_prices,
            'high': high_prices,
            'low': low_prices,
            'close': close_prices,
            'volume': volumes
        })
        
        return df
        
    def get_available_exchanges(self):
        """Obtener lista de exchanges disponibles"""
        exchanges = ['binance', 'bingx']
        exchanges.extend([ex for ex in ccxt.exchanges if ex not in exchanges])
        return exchanges
        
    def get_available_pairs(self, exchange):
        """Obtener pares disponibles para un exchange"""
        try:
            if exchange == 'binance':
                response = requests.get(f"{DEFAULT_BINANCE_API_URL}/api/v3/exchangeInfo")
                if response.status_code == 200:
                    data = response.json()
                    # Formatear como 'BTC/USDT'
                    pairs = []
                    for symbol in data['symbols']:
                        if symbol['status'] == 'TRADING':
                            base = symbol['baseAsset']
                            quote = symbol['quoteAsset']
                            pairs.append(f"{base}/{quote}")
                    return pairs
                else:
                    return self._get_default_pairs()
                    
            elif exchange == 'bingx':
                response = requests.get(f"{DEFAULT_BINGX_API_URL}/openApi/swap/v2/quote/contracts")
                if response.status_code == 200:
                    data = response.json()
                    if data['code'] == 0 and 'data' in data:
                        # Formatear como 'BTC/USDT'
                        pairs = [s['symbol'].replace('-', '/') for s in data['data']]
                        return pairs
                    else:
                        return self._get_default_pairs()
                else:
                    return self._get_default_pairs()
            
            elif exchange in self.ccxt_exchanges or self.init_ccxt_exchange(exchange):
                ex = self.ccxt_exchanges[exchange]
                ex.load_markets()
                return list(ex.markets.keys())
                
            else:
                return self._get_default_pairs()
                
        except Exception as e:
            print(f"Error al obtener pares para {exchange}: {str(e)}")
            return self._get_default_pairs()
            
    def _get_default_pairs(self):
        """Lista predeterminada de pares comunes"""
        return [
            'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 
            'ADA/USDT', 'XRP/USDT', 'DOT/USDT', 'AVAX/USDT',
            'DOGE/USDT', 'SHIB/USDT'
        ]
