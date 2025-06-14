import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import User
from app.models.exchange import Exchange
from app.core.security import get_password_hash

# Cliente de prueba
client = TestClient(app)

def get_auth_header(client, email="test@example.com", password="password"):
    """Helper para obtener un token de autenticación"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def setup_test_user_with_exchange(db: Session):
    """Helper para crear un usuario de prueba con un exchange"""
    # Crear usuario
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password"),
        full_name="Test User",
        is_active=True,
        user_level="basic"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Crear exchange para el usuario
    exchange = Exchange(
        user_id=user.id,
        name="Test Exchange",
        exchange_type="binance",
        api_key="test_key",
        api_secret="test_secret",
        is_active=True
    )
    db.add(exchange)
    db.commit()
    db.refresh(exchange)
    
    return user, exchange

def test_read_exchanges(test_db):
    """Test para verificar la obtención de exchanges del usuario"""
    # Preparar: Crear un usuario y exchange
    user, exchange = setup_test_user_with_exchange(test_db)
    
    # Obtener token
    headers = get_auth_header(client)
    
    # Ejecutar: Obtener exchanges
    response = client.get(
        "/api/v1/exchanges/",
        headers=headers
    )
    
    # Verificar: Comprobar que se obtienen los exchanges correctamente
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Test Exchange"
    assert response.json()[0]["exchange_type"] == "binance"
    assert response.json()[0]["api_key"] == "********"  # Verificar que está enmascarado

def test_create_exchange(test_db):
    """Test para verificar la creación de un nuevo exchange"""
    # Preparar: Crear un usuario
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password"),
        full_name="Test User",
        is_active=True,
        user_level="basic"
    )
    test_db.add(user)
    test_db.commit()
    
    # Obtener token
    headers = get_auth_header(client)
    
    # Ejecutar: Crear exchange
    response = client.post(
        "/api/v1/exchanges/",
        headers=headers,
        json={
            "name": "New Exchange",
            "exchange_type": "bybit",
            "api_key": "new_key",
            "api_secret": "new_secret",
            "is_active": True
        }
    )
    
    # Verificar: Comprobar que el exchange se creó correctamente
    assert response.status_code == 200
    assert response.json()["name"] == "New Exchange"
    assert response.json()["exchange_type"] == "bybit"
    
    # Verificar que existe en la base de datos
    exchange = test_db.query(Exchange).filter(Exchange.name == "New Exchange").first()
    assert exchange is not None
    assert exchange.user_id == user.id

def test_update_exchange(test_db):
    """Test para verificar la actualización de un exchange existente"""
    # Preparar: Crear un usuario y exchange
    user, exchange = setup_test_user_with_exchange(test_db)
    
    # Obtener token
    headers = get_auth_header(client)
    
    # Ejecutar: Actualizar exchange
    response = client.put(
        f"/api/v1/exchanges/{exchange.id}",
        headers=headers,
        json={
            "name": "Updated Exchange",
            "is_active": False
        }
    )
    
    # Verificar: Comprobar que el exchange se actualizó correctamente
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Exchange"
    assert response.json()["is_active"] == False
    
    # Verificar en la base de datos
    updated_exchange = test_db.query(Exchange).filter(Exchange.id == exchange.id).first()
    assert updated_exchange.name == "Updated Exchange"
    assert updated_exchange.is_active == False

def test_delete_exchange(test_db):
    """Test para verificar la eliminación de un exchange"""
    # Preparar: Crear un usuario y exchange
    user, exchange = setup_test_user_with_exchange(test_db)
    
    # Obtener token
    headers = get_auth_header(client)
    
    # Ejecutar: Eliminar exchange
    response = client.delete(
        f"/api/v1/exchanges/{exchange.id}",
        headers=headers
    )
    
    # Verificar: Comprobar que el exchange se eliminó correctamente
    assert response.status_code == 204
    
    # Verificar en la base de datos
    deleted_exchange = test_db.query(Exchange).filter(Exchange.id == exchange.id).first()
    assert deleted_exchange is None
