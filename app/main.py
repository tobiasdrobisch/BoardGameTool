from fastapi import FastAPI, Depends, HTTPException, status, Body, APIRouter
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import desc
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse, HTMLResponse
from .database import Base, engine, get_db, SessionLocal
from . import schemas, crud, utils, models
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

# Create tables
try:
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")
except Exception as e:
    print(f"Failed to create tables: {e}")
    raise

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        logging.debug("Token received: %s", token)
        payload = utils.decode_access_token(token)
        user_id = payload.get("user_id")
        print("Decoded user_id:", user_id)
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print("Token Error:", e)
        raise HTTPException(status_code=401, detail="Invalid token")
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/", response_class=HTMLResponse)
def root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/dashboard.html")
def dashboard():
    return FileResponse("static/dashboard.html")

@app.post("/start_kingdom_builder/")
def start_kingdom_builder(
        players: list[str] = Body(...),
        db: Session = Depends(get_db),
        current_user: schemas.UserRead = Depends(get_current_user)
):
    try:
        game_data = kingdom_builder.create_match()

        # Persist match in database
        game_in = schemas.GameCreate(**game_data)
        db_game = crud.create_match(db, game_in, current_user)

        # Persist players for the match
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

        # Attach numeric IDs to tasks for frontend
        tasks_with_ids = [{"id": idx, "name": task} for idx, task in enumerate(game_data["tasks"])]

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
        print("Error in start_kingdom_builder:", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}/", response_model=schemas.UserRead)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/users/", response_model=list[schemas.UserRead])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_users(db, skip=skip, limit=limit)

@app.post("/register/", response_model=schemas.UserRead, status_code=201)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already exists")
    if crud.get_user_by_username(db, user.name):
        raise HTTPException(status_code=400, detail="Username already exists")
    return crud.create_user(db, user)

@app.post("/login/", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    if not db_user or not utils.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username or password incorrect")
    access_token = utils.create_access_token(data={"user_id": db_user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me/", response_model=schemas.UserRead)
def read_me(current_user: schemas.UserRead = Depends(get_current_user)):
    return current_user

@app.delete("/users/me/", response_model=dict, status_code=200)
def delete_me(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    crud.delete_user(db, current_user.id)
    return {"msg": "User deleted successfully"}

@app.post("/matches/scores/")
def save_match_scores(payload: schemas.MatchScoresCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    match_players = crud.get_match_players_by_match_id(db, payload.match_id)
    if not match_players:
        raise HTTPException(status_code=404, detail="No players found for this game")

    username_to_obj = {mp.username_snapshot: mp for mp in match_players}

    for task_name, player_scores in payload.scores.items():
        for username, score in player_scores.items():
            if username not in username_to_obj:
                continue
            mp_obj = username_to_obj[username]
            result = crud.get_match_result_by_player(db, mp_obj.id)
            if not result:
                result = crud.create_match_result(db, mp_obj.id, total_score=0)
            crud.create_match_result_value(db, match_result_id=result.id, category=task_name, value=score)
            result.total_score += score
            db.commit()
            db.refresh(result)
    return {"status": "ok"}


@app.get("/matches/my")
def get_my_matches(db: Session = Depends(get_db), current_user=Depends(get_current_user)):

    # sort at backend for newest match desc
    matches = (
        db.query(models.Match)
        .filter(models.Match.created_by == current_user.id)
        .order_by(desc(models.Match.created_at))
        .all()
    )

    result = []

    for m in matches:
        match_players = db.query(models.MatchPlayer).filter(models.MatchPlayer.match_id == m.id).all()

        players_info = []
        scores = {}

        for mp in match_players:
            # Username + user_id for Frontend
            players_info.append({"username": mp.username_snapshot, "user_id": mp.user_id})

            # get score
            match_result = db.query(models.MatchResult).filter(models.MatchResult.match_player_id == mp.id).first()
            scores[mp.user_id] = {
                "username": mp.username_snapshot,
                "score": match_result.total_score if match_result else 0
            }

        result.append({
            "match_id": m.id,

            # Raw timestamp for sorting
            "created_at": m.created_at.isoformat(),

            # Pretty display date
            "date": m.created_at.strftime("%Y-%m-%d %H:%M"),

            "players": players_info, # list with username and user_id
            "player_count": len(players_info),
            "scores": scores,
        })

    return result


@app.get("/matches/{match_id}")
def get_match_detail(match_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    match = db.query(models.Match).filter(models.Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    match_players = db.query(models.MatchPlayer).filter(models.MatchPlayer.match_id == match_id).all()
    if not match_players:
        raise HTTPException(status_code=404, detail="No players found for this match")

    match_data = {
        "map": match.map,  # Adjust field name according to your model
        "island": match.island,
        "caves": match.caves,
        "capitols": match.capitols,
        "tasks": match.tasks,
        "players": {}
    }

    for mp in match_players:
        match_result = db.query(models.MatchResult).filter(models.MatchResult.match_player_id == mp.id).first()
        player_details = {}
        total_score = 0
        if match_result:
            values = db.query(models.MatchResultValue).filter(models.MatchResultValue.match_result_id == match_result.id).all()
            for v in values:
                player_details[v.category] = v.value
            total_score = match_result.total_score
        match_data["players"][mp.user_id] = {"username": mp.username_snapshot, "total": total_score, "details": player_details}

    return match_data
