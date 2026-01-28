from sqlalchemy.orm import Session
from . import models

BOARD_GAMES = [
    {
        "name": "Kingdom Builder",
        "min_players": 2,
        "max_players": 5,
        "description": "Base game",
    }
]

def seed_board_games(db: Session):
    for game in BOARD_GAMES:
        exists = db.query(models.BoardGame).filter(
            models.BoardGame.name == game["name"]
        ).first()

        if not exists:
            db.add(models.BoardGame(**game))
            print(f"Seeded board game: {game['name']}")

    db.commit()