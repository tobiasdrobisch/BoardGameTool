from datetime import datetime
from typing import Any, List, Dict, Optional

from pydantic import BaseModel, EmailStr, field_validator

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

    @field_validator("password")
    @classmethod
    def password_length(cls, v: str):
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password must not exceed 72 bytes")
        return v


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
    start_player_id: Optional[int] = None

class GameRead(BaseModel):
    """
    Placeholder schema for reading game data.
    """
    pass


class MatchScoresUpdate(BaseModel):
    scores: Dict[str, Dict[str, int]] # { "Task 1": { "Player1": 5, "Player2": 3 }, ... }

    model_config = {
        "json_schema_extra": {
            "example": {
                "scores": {
                    "task1": {
                        "player1": 0,
                        "player2": 0,
                        "player...": 0
                    },
                    "task2": {
                        "player1": 0,
                        "player2": 0,
                        "player...": 0
                    },
                    "task...": {
                        "player1": 0,
                        "player2": 0,
                        "player...": 0
                    }
                }
            }
        }
    }