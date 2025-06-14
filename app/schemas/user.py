from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

# Esquemas compartidos
class UserBase(BaseModel):
    email: EmailStr
    is_active: Optional[bool] = True
    full_name: Optional[str] = None
    user_level: Optional[str] = "basic"

# Esquemas para crear
class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    user_level: Optional[str] = None

# Esquemas para respuestas
class UserInDB(UserBase):
    id: int
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class User(UserInDB):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: list[str] = []
