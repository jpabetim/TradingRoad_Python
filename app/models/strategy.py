from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base

class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    description = Column(String)
    exchange_id = Column(Integer, ForeignKey("exchanges.id"))
    symbol = Column(String, nullable=False)  # Ejemplo: BTC/USDT
    timeframe = Column(String, nullable=False)  # 1m, 5m, 15m, 1h, etc.
    is_active = Column(Boolean, default=False)
    is_backtesting = Column(Boolean, default=False)
    is_live = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    params = Column(JSON, default={})
    performance = Column(JSON, default={})
    
    # Métricas de rendimiento
    total_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    profit_factor = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    
    # Relaciones
    user = relationship("User", back_populates="strategies")
    trades = relationship("Trade", back_populates="strategy")

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"))
    symbol = Column(String, nullable=False)
    order_type = Column(String, nullable=False)  # market, limit, etc.
    side = Column(String, nullable=False)  # buy, sell
    price = Column(Float)
    amount = Column(Float)
    fee = Column(Float, default=0.0)
    is_closed = Column(Boolean, default=False)
    entry_time = Column(DateTime, default=datetime.utcnow)
    exit_time = Column(DateTime)
    profit_loss = Column(Float, default=0.0)
    profit_loss_percent = Column(Float, default=0.0)
    notes = Column(String)
    
    # Relaciones
    strategy = relationship("Strategy", back_populates="trades")
