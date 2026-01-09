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

def create_match(db: Session, match: schemas.GameCreate, current_user):
    db_match = models.Match(
        board_game_id = match.board_game_id,
        tasks=match.tasks,
        map=match.map,
        island=match.island,
        caves=match.caves,
        capitols=match.capitols,
        created_by=current_user.id
    )
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match

def create_match_player(db: Session, match_id: int, player_name: str):
    db_player = models.MatchPlayer(match_id=match_id,
                                   username=player_name
                                   )
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player