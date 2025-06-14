from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, List, Optional

from app import models, schemas
from app.core import deps
from app.config import settings

router = APIRouter()

@router.get("/", response_model=List[schemas.Strategy])
def read_strategies(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    exchange_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Obtener todas las estrategias del usuario
    """
    # Iniciar la consulta base
    query = db.query(models.Strategy).filter(models.Strategy.user_id == current_user.id)
    
    # Aplicar filtros opcionales
    if exchange_id:
        query = query.filter(models.Strategy.exchange_id == exchange_id)
        
    if is_active is not None:
        query = query.filter(models.Strategy.is_active == is_active)
    
    # Obtener resultados paginados
    strategies = query.order_by(models.Strategy.created_at.desc()).offset(skip).limit(limit).all()
    
    return strategies

@router.post("/", response_model=schemas.Strategy)
def create_strategy(
    *,
    db: Session = Depends(deps.get_db),
    strategy_in: schemas.StrategyCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Crear nueva estrategia de trading
    """
    # Verificar si el exchange existe y pertenece al usuario
    exchange = db.query(models.Exchange).filter(
        models.Exchange.id == strategy_in.exchange_id,
        models.Exchange.user_id == current_user.id
    ).first()
    
    if not exchange:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exchange con id {strategy_in.exchange_id} no encontrado o no tiene permiso para usarlo",
        )
    
    # Verificar límites según nivel de usuario
    user_level = current_user.user_level
    user_strategies = (
        db.query(models.Strategy)
        .filter(models.Strategy.user_id == current_user.id)
        .count()
    )
    
    max_strategies = settings.USER_LEVELS.get(user_level, {}).get("max_strategies", 1)
    
    if user_strategies >= max_strategies and not current_user.is_superuser:
        raise HTTPException(
            status_code=400,
            detail=f"Has alcanzado el límite de estrategias para tu nivel de cuenta ({user_level})"
        )
    
    # Crear estrategia
    strategy = models.Strategy(
        **strategy_in.dict(),
        user_id=current_user.id,
        total_trades=0,
        win_rate=0.0,
        profit_factor=0.0,
        max_drawdown=0.0,
        performance={}
    )
    
    db.add(strategy)
    db.commit()
    db.refresh(strategy)
    
    return strategy

@router.get("/{strategy_id}", response_model=schemas.Strategy)
def read_strategy(
    *,
    db: Session = Depends(deps.get_db),
    strategy_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Obtener estrategia por ID
    """
    strategy = db.query(models.Strategy).filter(
        models.Strategy.id == strategy_id
    ).first()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estrategia no encontrada",
        )
    
    # Verificar permisos
    if strategy.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a esta estrategia",
        )
    
    return strategy

@router.put("/{strategy_id}", response_model=schemas.Strategy)
def update_strategy(
    *,
    db: Session = Depends(deps.get_db),
    strategy_id: int,
    strategy_in: schemas.StrategyUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Actualizar estrategia
    """
    strategy = db.query(models.Strategy).filter(
        models.Strategy.id == strategy_id
    ).first()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estrategia no encontrada",
        )
    
    # Verificar permisos
    if strategy.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar esta estrategia",
        )
    
    # Si se está actualizando el exchange_id, verificar que exista y pertenezca al usuario
    if strategy_in.exchange_id and strategy_in.exchange_id != strategy.exchange_id:
        exchange = db.query(models.Exchange).filter(
            models.Exchange.id == strategy_in.exchange_id,
            models.Exchange.user_id == current_user.id
        ).first()
        
        if not exchange:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exchange con id {strategy_in.exchange_id} no encontrado o no tiene permiso para usarlo",
            )
    
    # Actualizar campos
    update_data = strategy_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(strategy, field, value)
    
    db.add(strategy)
    db.commit()
    db.refresh(strategy)
    
    return strategy

@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_strategy(
    *,
    db: Session = Depends(deps.get_db),
    strategy_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Eliminar estrategia
    """
    strategy = db.query(models.Strategy).filter(
        models.Strategy.id == strategy_id
    ).first()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estrategia no encontrada",
        )
    
    # Verificar permisos
    if strategy.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar esta estrategia",
        )
    
    # Eliminar estrategia
    db.delete(strategy)
    db.commit()
    
    return None

@router.post("/{strategy_id}/trades", response_model=schemas.Trade)
def create_trade(
    *,
    db: Session = Depends(deps.get_db),
    strategy_id: int,
    trade_in: schemas.TradeCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Registrar un nuevo trade para una estrategia
    """
    # Verificar si la estrategia existe y pertenece al usuario
    strategy = db.query(models.Strategy).filter(
        models.Strategy.id == strategy_id,
        models.Strategy.user_id == current_user.id
    ).first()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estrategia no encontrada o no tiene permiso para acceder a ella",
        )
    
    # Crear el trade (asumiendo que existe el modelo Trade)
    trade = models.Trade(
        **trade_in.dict(),
        strategy_id=strategy_id,
        is_closed=False,
        entry_time=datetime.utcnow(),
        profit_loss=0.0,
        profit_loss_percent=0.0
    )
    
    db.add(trade)
    db.commit()
    db.refresh(trade)
    
    return trade

@router.get("/{strategy_id}/trades", response_model=List[schemas.Trade])
def read_trades(
    *,
    db: Session = Depends(deps.get_db),
    strategy_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Obtener todos los trades de una estrategia
    """
    # Verificar si la estrategia existe y pertenece al usuario
    strategy = db.query(models.Strategy).filter(
        models.Strategy.id == strategy_id,
        models.Strategy.user_id == current_user.id
    ).first()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estrategia no encontrada o no tiene permiso para acceder a ella",
        )
    
    # Obtener trades
    trades = (
        db.query(models.Trade)
        .filter(models.Trade.strategy_id == strategy_id)
        .order_by(models.Trade.entry_time.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return trades
