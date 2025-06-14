from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, List

from app import models, schemas
from app.core import deps
from app.config import settings

router = APIRouter()

@router.get("/", response_model=List[schemas.Exchange])
def read_exchanges(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Obtener todas las exchanges del usuario
    """
    # Si es superusuario, puede ver todas las exchanges
    if current_user.is_superuser:
        exchanges = db.query(models.Exchange).offset(skip).limit(limit).all()
    else:
        # Si no, solo ve sus propias exchanges
        exchanges = (
            db.query(models.Exchange)
            .filter(models.Exchange.user_id == current_user.id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    return exchanges

@router.post("/", response_model=schemas.Exchange)
def create_exchange(
    *,
    db: Session = Depends(deps.get_db),
    exchange_in: schemas.ExchangeCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Crear nueva conexión a exchange
    """
    # Verificar límites según nivel de usuario
    user_level = current_user.user_level
    user_exchanges = (
        db.query(models.Exchange)
        .filter(models.Exchange.user_id == current_user.id)
        .count()
    )
    
    max_exchanges = settings.USER_LEVELS.get(user_level, {}).get("max_exchanges", 1)
    
    if user_exchanges >= max_exchanges and not current_user.is_superuser:
        raise HTTPException(
            status_code=400,
            detail=f"Has alcanzado el límite de exchanges para tu nivel de cuenta ({user_level})"
        )
    
    # Validar si hay conexión a la exchange
    try:
        # Aquí se podría implementar la validación de credenciales con ccxt
        # Para simplificar, asumimos que son válidas
        exchange = models.Exchange(
            name=exchange_in.name,
            exchange_type=exchange_in.exchange_type,
            api_key=exchange_in.api_key,
            api_secret=exchange_in.api_secret,
            is_active=exchange_in.is_active,
            config=exchange_in.config,
            user_id=current_user.id,
        )
        db.add(exchange)
        db.commit()
        db.refresh(exchange)
        return exchange
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al conectar con el exchange: {str(e)}",
        )

@router.get("/{exchange_id}", response_model=schemas.Exchange)
def read_exchange(
    *,
    db: Session = Depends(deps.get_db),
    exchange_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Obtener exchange por ID
    """
    exchange = db.query(models.Exchange).filter(models.Exchange.id == exchange_id).first()
    
    if not exchange:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exchange no encontrado",
        )
    
    # Verificar permisos
    if exchange.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a este exchange",
        )
    
    return exchange

@router.put("/{exchange_id}", response_model=schemas.Exchange)
def update_exchange(
    *,
    db: Session = Depends(deps.get_db),
    exchange_id: int,
    exchange_in: schemas.ExchangeUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Actualizar exchange
    """
    exchange = db.query(models.Exchange).filter(models.Exchange.id == exchange_id).first()
    
    if not exchange:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exchange no encontrado",
        )
    
    # Verificar permisos
    if exchange.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar este exchange",
        )
    
    # Actualizar campos
    update_data = exchange_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(exchange, field, value)
    
    db.add(exchange)
    db.commit()
    db.refresh(exchange)
    return exchange

@router.delete("/{exchange_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exchange(
    *,
    db: Session = Depends(deps.get_db),
    exchange_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Eliminar exchange
    """
    exchange = db.query(models.Exchange).filter(models.Exchange.id == exchange_id).first()
    
    if not exchange:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exchange no encontrado",
        )
    
    # Verificar permisos
    if exchange.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar este exchange",
        )
    
    # Eliminar exchange
    db.delete(exchange)
    db.commit()
    
    # Cuando se usa status_code=204, no se debe devolver nada
