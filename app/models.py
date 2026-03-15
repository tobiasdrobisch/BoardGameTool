from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON,UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    board_games = relationship(
        "UserBoardGame",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # set foreign keys
    matches_created = relationship(
        "Match",
        back_populates="creator",
        foreign_keys="Match.created_by"
    )


class BoardGame(Base):
    __tablename__ = "board_games"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    min_players = Column(Integer, nullable=False)
    max_players = Column(Integer, nullable=False)
    description = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship(
        "UserBoardGame",
        back_populates="board_game",
        cascade="all, delete-orphan"
    )

    matches = relationship("Match", back_populates="board_game")


class UserBoardGame(Base):
    __tablename__ = "user_board_games"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    board_game_id = Column(Integer, ForeignKey("board_games.id"), primary_key=True)

    added_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="board_games")
    board_game = relationship("BoardGame", back_populates="users")


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    board_game_id = Column(Integer, ForeignKey("board_games.id"), nullable=False)

    caves = Column(String, nullable=False)
    capitols = Column(String, nullable=False)
    island = Column(String, nullable=False)

    tasks = Column(JSON, nullable=False)
    map = Column(JSON, nullable=False)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_player_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    board_game = relationship("BoardGame", back_populates="matches")

    # set foreign keys explicitly
    creator = relationship(
        "User",
        back_populates="matches_created",
        foreign_keys=[created_by]
    )

    start_player = relationship(
        "User",
        foreign_keys=[start_player_id]
    )

    players = relationship(
        "MatchPlayer",
        back_populates="match",
        cascade="all, delete-orphan"
    )

class MatchPlayer(Base):
    __tablename__ = "match_players"

    __table_args__ = (
        UniqueConstraint("match_id", "user_id", name="unique_match_player"),
    )

    id = Column(Integer, primary_key=True, index=True)

    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    username_snapshot = Column(String, nullable=False)

    seat_number = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    match = relationship("Match", back_populates="players")

    results = relationship(
        "MatchResult",
        back_populates="match_player",
        cascade="all, delete-orphan"
    )


class MatchResult(Base):
    __tablename__ = "match_results"

    id = Column(Integer, primary_key=True, index=True)

    match_player_id = Column(Integer, ForeignKey("match_players.id"), nullable=False)

    total_score = Column(Integer, nullable=False)
    rank = Column(Integer, nullable=True)
    is_winner = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    match_player = relationship("MatchPlayer", back_populates="results")

    values = relationship(
        "MatchResultValue",
        back_populates="match_result",
        cascade="all, delete-orphan"
    )


class MatchResultValue(Base):
    __tablename__ = "match_result_values"

    id = Column(Integer, primary_key=True, index=True)

    match_result_id = Column(Integer, ForeignKey("match_results.id"), nullable=False)

    category = Column(String, nullable=False)
    value = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    match_result = relationship("MatchResult", back_populates="values")