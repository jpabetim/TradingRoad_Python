"""
Utilidades para el análisis técnico y gestión de datos de trading
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import random

from app.utils.market_data import MarketDataClient

# Path to the exchanges configuration file
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                           "config", "exchanges.json")

# Try to load configuration
market_data_client = None
try:
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        market_data_client = MarketDataClient(config)
    else:
        print(f"Warning: Exchanges config not found at {config_path}, using default configuration")
        market_data_client = MarketDataClient()
except Exception as e:
    print(f"Error loading exchanges config: {str(e)}")
    market_data_client = MarketDataClient()

def get_candle_data(symbol, timeframe, exchange, limit=100):
    """
    Get OHLCV candle data for the specified symbol, timeframe, and exchange.
    
    Args:
        symbol: Trading pair (e.g., BTCUSDT)
        timeframe: Timeframe (e.g., 5m, 1h, 4h, 1d)
        exchange: Exchange to get data from (e.g., binance, bingx)
        limit: Maximum number of candles to return
        
    Returns:
        DataFrame with OHLCV data or None if error
    """
    try:
        # Standard formatting for symbols
        symbol_formatted = symbol
        if '/' not in symbol:
            # Try to format as 'BTC/USDT' if given as 'BTCUSDT'
            parts = []
            if 'USDT' in symbol:
                parts = [symbol.replace('USDT', ''), 'USDT']
            elif 'USD' in symbol:
                parts = [symbol.replace('USD', ''), 'USD']
            elif 'BTC' in symbol and symbol != 'BTC':
                parts = [symbol.replace('BTC', ''), 'BTC']
                
            if parts:
                symbol_formatted = f"{parts[0]}/{parts[1]}"
        
        # Standardize exchange name
        exchange_mapped = exchange.lower()
        if 'binance' in exchange_mapped and 'futures' in exchange_mapped:
            exchange_mapped = 'binance'
            
        # Get data from market_data_client
        if market_data_client:
            data = market_data_client.get_market_data(exchange_mapped, symbol_formatted, timeframe, limit)
            if not data.empty:
                return data
                
        # Fallback to sample data if no real data available
        return generate_sample_data(symbol, limit=limit)
            
    except Exception as e:
        print(f"Error in get_candle_data: {str(e)}")
        return None
        
def generate_sample_data(symbol="BTCUSDT", limit=100):
    """
    Generate sample OHLCV data for testing when real data is unavailable.
    
    Args:
        symbol: Trading pair to simulate
        limit: Number of candles to generate
        
    Returns:
        DataFrame with simulated OHLCV data
    """
    # Determine base price and volatility based on symbol
    if "BTC" in symbol:
        base_price = 65000 + random.uniform(-2000, 2000) 
        volatility = 1.5
    elif "ETH" in symbol:
        base_price = 2500 + random.uniform(-200, 200)
        volatility = 2.0
    elif "SOL" in symbol:
        base_price = 150 + random.uniform(-10, 10)
        volatility = 4.0
    else:
        base_price = 100 + random.uniform(-10, 10)
        volatility = 3.0
        
    # Set trend (slightly bearish or bullish)
    trend = random.uniform(-0.2, 0.2)
    
    # Generate dates (going back from now)
    end_time = datetime.now()
    start_time = end_time - timedelta(days=limit)
    dates = [start_time + timedelta(days=i) for i in range(limit)]
    
    # Initialize first price
    current_price = base_price
    
    # Lists for OHLCV data
    opens = []
    highs = []
    lows = []
    closes = []
    volumes = []
    
    # Generate candle data
    for i in range(limit):
        # Calculate price change with random walk + trend
        price_change = np.random.normal(trend, volatility) * current_price / 100
        
        # Set open price (close of previous candle or base price for first candle)
        open_price = current_price if i > 0 else base_price
        
        # Calculate close with the random change
        close_price = open_price + price_change
        
        # Calculate high and low with added noise
        high_price = max(open_price, close_price) + abs(np.random.normal(0, volatility/2) * open_price / 100)
        low_price = min(open_price, close_price) - abs(np.random.normal(0, volatility/2) * open_price / 100)
        
        # Generate volume (higher on larger price movements)
        volume = abs(price_change) * random.uniform(8000, 15000) / volatility
        
        # Save values
        opens.append(open_price)
        highs.append(high_price)
        lows.append(low_price)
        closes.append(close_price)
        volumes.append(volume)
        
        # Update current price for next iteration
        current_price = close_price
    
    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': dates,
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes,
        'volume': volumes
    })
    
    return df
        
def calculate_indicators(df, indicators=None):
    """
    Calculate technical indicators on OHLCV data.
    
    Args:
        df: DataFrame with OHLCV data
        indicators: Dictionary with indicators to calculate and their parameters
        
    Returns:
        DataFrame with added indicator columns
    """
    if indicators is None:
        indicators = {
            'sma': [20, 50, 200],
            'ema': [9, 21],
            'rsi': [14],
            'macd': {'fast': 12, 'slow': 26, 'signal': 9}
        }
        
    result_df = df.copy()
    
    # Simple Moving Averages
    if 'sma' in indicators:
        for period in indicators['sma']:
            result_df[f'sma_{period}'] = result_df['close'].rolling(window=period).mean()
            
    # Exponential Moving Averages
    if 'ema' in indicators:
        for period in indicators['ema']:
            result_df[f'ema_{period}'] = result_df['close'].ewm(span=period, adjust=False).mean()
            
    # Relative Strength Index
    if 'rsi' in indicators:
        for period in indicators['rsi']:
            delta = result_df['close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            avg_gain = gain.rolling(window=period).mean()
            avg_loss = loss.rolling(window=period).mean()
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            result_df[f'rsi_{period}'] = rsi
            
    # MACD
    if 'macd' in indicators:
        fast = indicators['macd']['fast']
        slow = indicators['macd']['slow']
        signal_period = indicators['macd']['signal']
        
        fast_ema = result_df['close'].ewm(span=fast, adjust=False).mean()
        slow_ema = result_df['close'].ewm(span=slow, adjust=False).mean()
        
        result_df['macd_line'] = fast_ema - slow_ema
        result_df['macd_signal'] = result_df['macd_line'].ewm(span=signal_period, adjust=False).mean()
        result_df['macd_histogram'] = result_df['macd_line'] - result_df['macd_signal']
        
    return result_df
