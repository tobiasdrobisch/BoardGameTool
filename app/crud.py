from sqlalchemy.orm import Session
from . import models, schemas, utils

def create_user(db: Session, user: schemas.UserCreate):
    hashed_pw = utils.hash_password(user.password)

    db_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_pw
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, name: str):
    return db.query(models.User).filter(models.User.name == name).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def update_user_info():
    pass

def delete_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        return None

    db.delete(user)
    db.commit()
    return user

def create_match(db: Session, game_data: dict, current_user, start_player_id):

    # dict → Pydantic Model
    match = schemas.GameCreate(**game_data, start_player_id=start_player_id)

    db_match = models.Match(
        board_game_id = match.board_game_id,
        tasks=match.tasks,
        map=match.map,
        island=match.island,
        caves=match.caves,
        capitols=match.capitols,
        created_by=current_user.id,
        start_player_id=start_player_id
    )
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match


def create_match_player(db: Session, match_id: int, user_id: int, username_snapshot: str):
    db_player = models.MatchPlayer(
        match_id=match_id,
        user_id=user_id,
        username_snapshot=username_snapshot
    )
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

# Create a MatchResult row for a player
def create_match_result(db: Session, match_player_id: int, total_score: int = 0) -> models.MatchResult:
    result = models.MatchResult(
        match_player_id=match_player_id,
        total_score=total_score
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result

# Create a MatchResultValue row for a specific task/category
def create_match_result_value(
    db: Session,
    match_result_id: int,
    category: str,
    value: int
) -> models.MatchResultValue:
    result_value = models.MatchResultValue(
        match_result_id=match_result_id,
        category=category,
        value=value
    )
    db.add(result_value)
    db.commit()
    db.refresh(result_value)
    return result_value

# Get all players for a specific match
def get_match_players_by_match_id(db: Session, match_id: int):
    return db.query(models.MatchPlayer).filter(models.MatchPlayer.match_id == match_id).all()

# Optional: get a MatchResult for a given player if it exists
def get_match_result_by_player(db: Session, match_player_id: int):
    return db.query(models.MatchResult).filter(models.MatchResult.match_player_id == match_player_id).first()


