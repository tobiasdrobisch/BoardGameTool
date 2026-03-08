from fastapi import FastAPI, Depends, HTTPException, status, Body, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse, HTMLResponse
from . import schemas, crud, utils, models
from .database import Base, engine, get_db, SessionLocal
from games import kingdom_builder
import logging
from .seed import seed_board_games
from contextlib import asynccontextmanager

# --- lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup")
    db = SessionLocal()
    try:
        seed_board_games(db)
    finally:
        db.close()
    yield
    print("Application shutdown")

# --- app creation ---
app = FastAPI(lifespan=lifespan)
router = APIRouter()

origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "https://boardgametool.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/script", StaticFiles(directory="script"), name="script")
app.mount("/locales", StaticFiles(directory="locales"), name="locales")

# Create tables
try:
    Base.metadata.create_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")
except Exception as e:
    print(f"Failed to create tables: {e}")
    raise

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        logging.debug("Token received: %s", token)
        payload = utils.decode_access_token(token)
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/", response_class=HTMLResponse)
def root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/dashboard.html")
def dashboard():
    response = FileResponse("static/dashboard.html")
    response.headers["Cache-Control"] = "no-store"
    return response

@app.post("/start_kingdom_builder")
def start_kingdom_builder(
    players: list[str] = Body(...),
    db: Session = Depends(get_db),
    current_user: schemas.UserRead = Depends(get_current_user)
):
    try:
        game_data = kingdom_builder.create_match()
        game_in = schemas.GameCreate(**game_data)
        db_game = crud.create_match(db, game_in, current_user)

        created_players = []
        for name in players:
            user = crud.get_user_by_username(db, name)

            crud.create_match_player(
                db=db,
                match_id=db_game.id,
                user_id=user.id,
                username_snapshot=user.name
            )
            created_players.append(name)

        tasks_with_ids = [
            {"id": idx, "name": task}
            for idx, task in enumerate(game_data["tasks"])
        ]

        return {
            "match_id": db_game.id,
            "board_game_id": game_data["board_game_id"],
            "map": game_data["map"],
            "island": game_data["island"],
            "caves": game_data["caves"],
            "capitols": game_data["capitols"],
            "players": created_players,
            "tasks": tasks_with_ids
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}", response_model=schemas.UserRead)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/users", response_model=list[schemas.UserRead])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_users(db, skip=skip, limit=limit)

@app.post("/register", response_model=schemas.UserRead, status_code=201)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already exists")
    if crud.get_user_by_username(db, user.name):
        raise HTTPException(status_code=400, detail="Username already exists")
    return crud.create_user(db, user)

@app.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    db_user = crud.get_user_by_username(db, form_data.username)

    if not db_user or not utils.verify_password(
        form_data.password,
        db_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username or password incorrect"
        )

    access_token = utils.create_access_token(
        data={"user_id": db_user.id}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/me", response_model=schemas.UserRead)
def read_me(current_user: schemas.UserRead = Depends(get_current_user)):
    return current_user

@app.delete("/users/me", response_model=dict)
def delete_me(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    crud.delete_user(db, current_user.id)
    return {"msg": "User deleted successfully"}

@app.get("/users/me/boardgames")
def get_my_boardgames(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return (
        db.query(models.BoardGame)
        .join(models.UserBoardGame)
        .filter(models.UserBoardGame.user_id == current_user.id)
        .all()
    )

@app.delete("/users/me/boardgames/{board_game_id}")
def remove_boardgame_from_user(
    board_game_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    entry = (
        db.query(models.UserBoardGame)
        .filter(
            models.UserBoardGame.user_id == current_user.id,
            models.UserBoardGame.board_game_id == board_game_id
        )
        .first()
    )

    if not entry:
        raise HTTPException(status_code=404, detail="Game not assigned")

    db.delete(entry)
    db.commit()
    return {"message": "Board game removed"}

@app.post("/users/me/boardgames/{board_game_id}")
def add_boardgame_to_user(
    board_game_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    game = db.query(models.BoardGame).filter(models.BoardGame.id == board_game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Board game not found")

    existing = (
        db.query(models.UserBoardGame)
        .filter(
            models.UserBoardGame.user_id == current_user.id,
            models.UserBoardGame.board_game_id == board_game_id
        )
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Game already added")

    user_game = models.UserBoardGame(
        user_id=current_user.id,
        board_game_id=board_game_id
    )

    db.add(user_game)
    db.commit()
    return {"message": "Board game added"}

@app.get("/matches/my")
def get_my_matches(db: Session = Depends(get_db),
                   current_user=Depends(get_current_user)):

    matches = (
        db.query(models.Match)
        .filter(models.Match.created_by == current_user.id)
        .order_by(desc(models.Match.created_at))
        .all()
    )

    result = []

    for m in matches:
        match_players = db.query(models.MatchPlayer).filter(
            models.MatchPlayer.match_id == m.id
        ).all()

        players_info = []
        scores = {}

        for mp in match_players:
            players_info.append({
                "username": mp.username_snapshot,
                "user_id": mp.user_id
            })

            match_result = db.query(models.MatchResult).filter(
                models.MatchResult.match_player_id == mp.id
            ).first()

            scores[mp.user_id] = {
                "username": mp.username_snapshot,
                "score": match_result.total_score if match_result else 0
            }

        result.append({
            "match_id": m.id,
            "created_at": m.created_at.isoformat(),
            "date": m.created_at.strftime("%Y-%m-%d %H:%M"),
            "players": players_info,
            "player_count": len(players_info),
            "scores": scores,
        })

    return result

@app.get("/matches/{match_id}")
def get_match_detail(match_id: int,
                     db: Session = Depends(get_db),
                     current_user=Depends(get_current_user)):

    match = db.query(models.Match).filter(models.Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    match_players = db.query(models.MatchPlayer).filter(
        models.MatchPlayer.match_id == match_id
    ).all()

    if not match_players:
        raise HTTPException(status_code=404, detail="No players found")

    match_data = {
        "match_id":match.id,
        "map": match.map,
        "island": match.island,
        "caves": match.caves,
        "capitols": match.capitols,
        "tasks": match.tasks,
        "players": {}
    }

    for mp in match_players:
        match_result = db.query(models.MatchResult).filter(
            models.MatchResult.match_player_id == mp.id
        ).first()

        player_details = {}
        tasks = match.tasks if match.tasks else []

        for task in tasks:
            player_details[task] = 0

        total_score = 0
        if match_result:
            values = db.query(models.MatchResultValue).filter(
                models.MatchResultValue.match_result_id == match_result.id
            ).all()

            for v in values:
                player_details[v.category] = v.value

            total_score = match_result.total_score

        match_data["players"][mp.user_id] = {
            "username": mp.username_snapshot,
            "total": total_score,
            "details": player_details
        }

    return match_data

@app.patch("/matches/{match_id}/scores")
def update_match_scores(
    match_id: int,
    payload: schemas.MatchScoresUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    match = db.query(models.Match).filter(
        models.Match.id == match_id
    ).first()

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    if match.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    match_players = db.query(models.MatchPlayer).filter(
        models.MatchPlayer.match_id == match_id
    ).all()

    username_to_obj = {mp.username_snapshot: mp for mp in match_players}

    # Update values and create MatchResult if missing
    for task_name, player_scores in payload.scores.items():
        for username, score in player_scores.items():
            if username not in username_to_obj:
                continue

            mp_obj = username_to_obj[username]

            result = db.query(models.MatchResult).filter(
                models.MatchResult.match_player_id == mp_obj.id
            ).first()

            if not result:
                result = models.MatchResult(match_player_id=mp_obj.id, total_score=0)
                db.add(result)
                db.flush()  # make sure result.id exists

            value_entry = db.query(models.MatchResultValue).filter(
                models.MatchResultValue.match_result_id == result.id,
                models.MatchResultValue.category == task_name
            ).first()

            if value_entry:
                value_entry.value = score
            else:
                db.add(models.MatchResultValue(
                    match_result_id=result.id,
                    category=task_name,
                    value=score
                ))
    db.flush()
    db.expire_all()

    # Aggregation
    totals = (
        db.query(
            models.MatchResult.id,
            func.sum(models.MatchResultValue.value)
        )
        .join(models.MatchResultValue)
        .group_by(models.MatchResult.id)
        .all()
    )


    total_map = {r[0]: r[1] or 0 for r in totals}

    match_results = db.query(models.MatchResult).filter(
        models.MatchResult.match_player_id.in_(
            db.query(models.MatchPlayer.id)
            .filter(models.MatchPlayer.match_id == match_id)
        )
    ).all()

    for result in match_results:
        result.total_score = total_map.get(result.id, 0)

    db.commit()

    # reset cache and get new data with next query
    db.expire_all()

    return {"status": "updated"}

@app.get("/boardgames")
def get_all_boardgames(db: Session = Depends(get_db)):
    return db.query(models.BoardGame).all()