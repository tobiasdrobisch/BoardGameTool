from datetime import datetime
from typing import Any, List

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """
    Base user schema with common attributes.
    """
    name: str
    email: EmailStr


class UserCreate(BaseModel):
    """
    Schema used for user registration.
    """
    name: str
    email: EmailStr
    password: str


class UserRead(BaseModel):
    """
    Schema used for returning user data.
    """
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """
    Schema used for user login.
    """
    username: str
    password: str


class Token(BaseModel):
    """
    Schema for JWT token responses.
    """
    access_token: str
    token_type: str


class UserDelete(BaseModel):
    """
    Placeholder schema for user deletion.
    """
    pass


class GameCreate(BaseModel):
    """
    Schema used for creating a new game.
    """
    caves: str
    capitols: str
    island: str
    map: List[List[Any]]
    tasks: List[str]
    board_game_id: int


class GameRead(BaseModel):
    """
    Placeholder schema for reading game data.
    """
    pass
