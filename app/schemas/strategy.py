from pydantic import BaseModel, validator
from typing import Optional, Dict, Any, List
from datetime import datetime

# Esquemas compartidos
class StrategyBase(BaseModel):
    name: str
    description: Optional[str] = None
    exchange_id: int
    symbol: str
    timeframe: str
    is_active: bool = False
    is_backtesting: bool = False
    is_live: bool = False
    params: Optional[Dict[str, Any]] = {}

# Esquemas para crear y actualizar
class StrategyCreate(StrategyBase):
    @validator('timeframe')
    def validate_timeframe(cls, v):
        allowed_timeframes = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"]
        if v not in allowed_timeframes:
            raise ValueError(f"Timeframe debe ser uno de: {', '.join(allowed_timeframes)}")
        return v

class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    exchange_id: Optional[int] = None
    symbol: Optional[str] = None
    timeframe: Optional[str] = None
    is_active: Optional[bool] = None
    is_backtesting: Optional[bool] = None
    is_live: Optional[bool] = None
    params: Optional[Dict[str, Any]] = None

# Esquemas para respuestas
class StrategyInDB(StrategyBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    total_trades: int
    win_rate: float
    profit_factor: float
    max_drawdown: float
    performance: Dict[str, Any]

    class Config:
        orm_mode = True

class Strategy(StrategyInDB):
    pass

# Esquemas para trades
class TradeBase(BaseModel):
    strategy_id: int
    symbol: str
    order_type: str
    side: str
    price: Optional[float] = None
    amount: float
    fee: Optional[float] = 0.0
    notes: Optional[str] = None

class TradeCreate(TradeBase):
    pass

class TradeUpdate(BaseModel):
    is_closed: Optional[bool] = None
    exit_time: Optional[datetime] = None
    profit_loss: Optional[float] = None
    profit_loss_percent: Optional[float] = None
    notes: Optional[str] = None

class TradeInDB(TradeBase):
    id: int
    is_closed: bool
    entry_time: datetime
    exit_time: Optional[datetime] = None
    profit_loss: float
    profit_loss_percent: float

    class Config:
        orm_mode = True

class Trade(TradeInDB):
    pass
