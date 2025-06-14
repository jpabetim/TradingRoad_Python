from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime

# Esquemas compartidos
class ExchangeBase(BaseModel):
    name: str
    exchange_type: str
    is_active: bool = True
    config: Optional[Dict[str, Any]] = {}

# Esquemas para crear y actualizar
class ExchangeCreate(ExchangeBase):
    api_key: str
    api_secret: str
    
    @validator('exchange_type')
    def validate_exchange_type(cls, v):
        allowed_types = ["binance", "bingx", "bybit", "bitget", "coinbase", "kraken"]
        if v.lower() not in allowed_types:
            raise ValueError(f"Exchange type debe ser uno de: {', '.join(allowed_types)}")
        return v.lower()

class ExchangeUpdate(BaseModel):
    name: Optional[str] = None
    exchange_type: Optional[str] = None
    is_active: Optional[bool] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

# Esquemas para respuestas
class ExchangeInDB(ExchangeBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Exchange(ExchangeInDB):
    # Excluir datos sensibles
    api_key: str = "********"
    api_secret: str = "********"
