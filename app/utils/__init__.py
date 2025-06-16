"""
Utilidades para la aplicación TradingRoad.

Este paquete contiene módulos para obtención de datos de mercado y análisis técnico.
"""

from .market_data import MarketDataClient
from .technical_analysis import generate_analysis

__all__ = ['MarketDataClient', 'generate_analysis']
