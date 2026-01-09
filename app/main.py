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
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse, JSONResponse
from datetime import timedelta

from .database import Base, engine, get_db
from . import schemas, crud, utils
from games import kingdom_builder

app = FastAPI()

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
        print("Token erhalten:", token)  # debug
        payload = utils.decode_access_token(token)
        user_id = payload.get("user_id")
        print("Decoded user_id:", user_id)
        if user_id is None:
            raise HTTPException(status_code=401, detail="wrong Token")
    except Exception as e:
        print("Token Fehler:", e)
        raise HTTPException(status_code=401, detail="wrong Token")
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/")
def root():
    return FileResponse("static/index.html")

@app.get("/dashboard.html")
def dashboard():
    return FileResponse("static/dashboard.html")

@app.post("/start_kingdom_builder/")
#def start_kingdom_builder(payload: schemas.StartGameRequest = Body(...), db: Session = Depends(get_db),current_user: schemas.UserRead = Depends(get_current_user)):
def start_kingdom_builder(players: list[str] = Body(...), db: Session = Depends(get_db),current_user: schemas.UserRead = Depends(get_current_user)):


    try:
        game_data = kingdom_builder.create_match()

        # create game
        game_in = schemas.GameCreate(**game_data)
        db_game = crud.create_match(db, game_in, current_user)

        for name in players:
            print(f"Versuch, player {name} hinzuzufügen")
            obj = crud.create_match_player(db=db, match_id=db_game.id, player_name=name)
            print("Objekt erstellt:", obj)

        #db.commit()

        return {"message": "Game erstellt", "game_id": db_game.id}
    except Exception as e:
        print("FEHLER in start_kingdom_builder:", e)
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/users/", response_model=schemas.UserRead)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.create_user(db, user)
    return db_user


@app.get("/users/{user_id}", response_model=schemas.UserRead)
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
    return crud.create_user(db, user)

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

@app.delete("/users/me", response_model=dict, status_code=200, summary="Delete your account")
def delete_me(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    crud.delete_user(db, current_user.id)
    return {"msg": "User deleted successfully"}


