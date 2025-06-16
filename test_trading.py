#!/usr/bin/env python3
"""
Script para probar los componentes de trading sin iniciar toda la aplicación web.
"""
import os
import sys
import json
import pandas as pd
from datetime import datetime

# Agregar directorio raíz al path para importar módulos propios
root_dir = os.path.abspath(os.path.dirname(__file__))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# Importar componentes necesarios
from app.utils.market_data import MarketDataClient
from app.utils.technical_analysis import generate_analysis

def test_trading_components():
    """Prueba los componentes clave del sistema de trading."""
    print("===== TEST DE COMPONENTES DE TRADING =====")
    
    # Cargar configuración de exchanges si existe
    config_path = os.path.join(root_dir, 'config', 'exchanges.json')
    config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            print("✅ Configuración de exchanges cargada correctamente")
        except Exception as e:
            print(f"⚠️ Error al cargar configuración de exchanges: {e}")
            print("Continuando sin configuración...")
    
    # Crear cliente de datos de mercado
    market_client = MarketDataClient(config)
    
    # Probar obtener datos de mercado
    exchange = "binance"
    symbol = "BTC/USDT"
    timeframe = "1h"
    limit = 100
    
    print(f"\nObteniendo datos de {exchange} para {symbol} en timeframe {timeframe}...")
    try:
        df = market_client.get_market_data(exchange=exchange, symbol=symbol, timeframe=timeframe, limit=limit)
        if df is not None and not df.empty:
            print(f"✅ Éxito! Se obtuvieron {len(df)} filas de datos OHLCV")
            print(df.head())
            
            # Probar análisis técnico
            print("\nGenerando análisis técnico...")
            analysis = generate_analysis(df, symbol, timeframe)
            if analysis:
                print("✅ Éxito! Análisis técnico generado correctamente")
                print("Primeros 500 caracteres del análisis:")
                print(analysis[:500] + "...")
            else:
                print("❌ Error al generar el análisis técnico")
        else:
            print("❌ Error: No se obtuvieron datos o el DataFrame está vacío")
    except Exception as e:
        print(f"❌ Error al obtener datos: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_trading_components()
