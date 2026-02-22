#ORM-Models


from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class BoardGame(Base):
    __tablename__ = "board_games"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    min_players = Column(Integer, nullable=False)
    max_players = Column(Integer, nullable=False)
    description = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    board_game_id = Column(Integer, ForeignKey("board_games.id"), nullable=False)
    caves = Column(String, nullable=False, unique=False)
    capitols = Column(String, unique=False, nullable=False)
    island = Column(String, nullable=False, unique=False)
    tasks = Column(JSON, nullable=False, unique=False)
    map = Column(JSON, nullable=False, unique=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MatchPlayer(Base):
    __tablename__ = "match_players"

    id = Column(Integer, primary_key=True, index=True)

    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Optional snapshot (recommended)
    username_snapshot = Column(String, nullable=False)

    seat_number = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MatchResult(Base):
    __tablename__ = "match_results"

    id = Column(Integer, primary_key=True, index=True)
    match_player_id = Column(Integer, ForeignKey("match_players.id"), nullable=False)

    total_score = Column(Integer, nullable=False)
    rank = Column(Integer, nullable=True)
    is_winner = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MatchResultValue(Base):
    __tablename__ = "match_result_values"

    id = Column(Integer, primary_key=True, index=True)
    match_result_id = Column(Integer, ForeignKey("match_results.id"), nullable=False)

    category = Column(String, nullable=False)  # z. B. "Straßen", "Burgen", "Bonus"
    value = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

