#   Get started

# 1. postgresql server running
# -> on windows + r: services.msc
# -> searching for "postgresql-x.x" → "running" / "start"

# 2. start fast api server in terminal with
#   -> uvicorn app.main:app --reload (in .venv)!
#   close fast api server with ctrl + c
#
# server on http://127.0.0.1:8000
# doc on http://127.0.0.1:8000/docs for post/get tryout etc.
#
# POST /register/ → JSON: { "name": "...", "email": "...", "password": "..." }
# POST /login/ → JSON: { "email": "...", "password": "..." } → receive token
# GET /me/ → Header Authorization: Bearer <token> → user-data

# Fast Api
# Routing
# Create Databases


from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from datetime import timedelta
from fastapi import APIRouter
from .database import Base, engine, get_db
from . import schemas, crud, utils
from games import kingdom_builder
import os, logging

app = FastAPI()
router = APIRouter()

origins = [
    "http://127.0.0.1:8000",             # local frontend
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,   # allowed domains
    allow_credentials=True,  # Cookies / Auth
    allow_methods=["*"],     # GET, POST, PUT, DELETE ...
    allow_headers=["*"],     # all headers
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Create tables if not existing
try:
    Base.metadata.create_all(bind=engine)
    print("Table created successfully.")
except Exception as e:
    print(f"Failed to create table: {e}")
    raise

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        print("Token received:", token)  # debug
        payload = utils.decode_access_token(token)
        user_id = payload.get("user_id")
        print("Decoded user_id:", user_id)
        if user_id is None:
            raise HTTPException(status_code=401, detail="wrong Token")
    except Exception as e:
        print("Token Error:", e)
        raise HTTPException(status_code=401, detail="wrong Token")
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# dynamically change backend destination depending on localhost or rendering live on render.com
@app.get("/", response_class=HTMLResponse)
def root():
    index_path = os.path.join("static", "index.html")

    # open index.html
    with open(index_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # set API_URL dynamically
    # local: 127.0.0.1:8000
    # live on Render: same origin like backend
    host_env = os.environ.get("HOST", "")
    api_url = "http://127.0.0.1:8000" if "127.0.0.1" in host_env else "https://boardgametool.onrender.com"

    # replace placeholder in index.html
    html_content = html_content.replace("{{API_URL}}", api_url)

    return HTMLResponse(content=html_content)


@app.get("/dashboard.html")
def dashboard():
    return FileResponse("static/dashboard.html")

@app.post("/start_kingdom_builder/")
#def start_kingdom_builder(payload: schemas.StartGameRequest = Body(...), db: Session = Depends(get_db),current_user: schemas.UserRead = Depends(get_current_user)):
def start_kingdom_builder(
        players: list[str] = Body(...),
        db: Session = Depends(get_db),
        current_user: schemas.UserRead = Depends(get_current_user)
):
    # Generate random match configuration
    try:
        game_data = kingdom_builder.create_match()

        # Persist match in database
        game_in = schemas.GameCreate(**game_data)
        db_game = crud.create_match(db, game_in, current_user)

        # Persist players for the match
        created_players = []
        for name in players:
            crud.create_match_player(
                db=db,
                match_id=db_game.id,
                username=name
            )
            created_players.append(name)
            print(f"Player {name} added")

        # Attach numeric IDs to tasks for frontend usage
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
        print("ERROR in start_kingdom_builder:", e)
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/users/", response_model=schemas.UserRead)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.create_user(db, user)
    return db_user


@app.get("/users/{user_id}/", response_model=schemas.UserRead)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/users/", response_model=list[schemas.UserRead])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_users(db, skip=skip, limit=limit)


# ----------------- Registration -----------------
@app.post("/register/", response_model=schemas.UserRead)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):


    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already exists")
    if crud.get_user_by_username(db, user.name):
        raise HTTPException(status_code=400, detail="Username already exists")
    try:
        new_user = crud.create_user(db, user)
        return {"msg": "User registered successfully", "user_id": new_user.id}
    except Exception as e:
        logging.error(f"Registration failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {e}"
        )

# ----------------- Login -----------------
@app.post("/login/", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    if not db_user or not utils.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Username or password incorrect")
    access_token = utils.create_access_token(data={"user_id": db_user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me/", response_model=schemas.UserRead)
def read_me(current_user: schemas.UserRead = Depends(get_current_user)):
    return current_user

@app.delete("/users/me/", response_model=dict, status_code=200, summary="Delete your account")
def delete_me(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    crud.delete_user(db, current_user.id)
    return {"msg": "User deleted successfully"}

@app.post("/matches/scores/")
def save_match_scores(
    payload: schemas.MatchScoresCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    """
    Store match scores for each player and task.
    """
    # Get all match_player entries for this game
    match_players = crud.get_match_players_by_match_id(db, payload.match_id)
    if not match_players:
        raise HTTPException(status_code=404, detail="No players found for this game")

    # Map username -> DB object
    username_to_obj = {mp.username: mp for mp in match_players}

    for task_name, player_scores in payload.scores.items():
        for username, score in player_scores.items():
            if username not in username_to_obj:
                continue

            mp_obj = username_to_obj[username]

            # Check or create MatchResult
            result = crud.get_match_result_by_player(db, mp_obj.id)
            if not result:
                result = crud.create_match_result(db, mp_obj.id, total_score=0)

            # Create MatchResultValue
            crud.create_match_result_value(db, match_result_id=result.id, category=task_name, value=score)

            # Update total score
            result.total_score += score
            db.commit()
            db.refresh(result)

    return {"status": "ok"}
