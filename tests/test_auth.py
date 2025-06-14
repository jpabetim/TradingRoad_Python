import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import Base
from app.core.deps import get_db
from app.models.user import User
from app.core.security import get_password_hash

# Crear base de datos en memoria para las pruebas
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Sobreescribir la dependencia get_db
@pytest.fixture
def test_db():
    # Crear tablas en la base de datos de prueba
    Base.metadata.create_all(bind=engine)
    
    # Crear una sesión de prueba
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        # Limpiar base de datos después de las pruebas
        Base.metadata.drop_all(bind=engine)

# Sobreescribir la dependencia get_db para usar la sesión de prueba
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Cliente de prueba
client = TestClient(app)

def setup_test_user(db):
    """Helper para crear un usuario de prueba"""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password"),
        full_name="Test User",
        is_active=True,
        user_level="basic"
    )
    db.add(user)
    db.commit()
    return user

def test_login(test_db):
    """Test para verificar el endpoint de login"""
    # Preparar: Crear un usuario de prueba
    setup_test_user(test_db)
    
    # Ejecutar: Intentar login
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "password"}
    )
    
    # Verificar: Comprobar que el login es exitoso
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_register(test_db):
    """Test para verificar el endpoint de registro"""
    # Ejecutar: Registrar un nuevo usuario
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "New User",
            "is_active": True,
            "user_level": "basic"
        }
    )
    
    # Verificar: Comprobar que el registro es exitoso
    assert response.status_code == 200
    assert response.json()["email"] == "newuser@example.com"
    assert response.json()["full_name"] == "New User"
    
    # Verificar que el usuario existe en la base de datos
    db_user = test_db.query(User).filter(User.email == "newuser@example.com").first()
    assert db_user is not None
    assert db_user.is_active == True

def test_login_wrong_password(test_db):
    """Test para verificar que no se puede hacer login con contraseña incorrecta"""
    # Preparar: Crear un usuario de prueba
    setup_test_user(test_db)
    
    # Ejecutar: Intentar login con contraseña incorrecta
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "wrong_password"}
    )
    
    # Verificar: Comprobar que el login falla
    assert response.status_code == 401

def test_me_endpoint(test_db):
    """Test para verificar el endpoint /me que requiere autenticación"""
    # Preparar: Crear un usuario y obtener token
    setup_test_user(test_db)
    
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "password"}
    )
    token = login_response.json()["access_token"]
    
    # Ejecutar: Obtener información del usuario autenticado
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Verificar: Comprobar que se obtiene la información correcta
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
