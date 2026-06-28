from pathlib import Path
from contextlib import asynccontextmanager
import time
from sqlalchemy.exc import OperationalError

from celery.result import AsyncResult
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel
from prometheus_fastapi_instrumentator import Instrumentator

from api.crud import (
    crud_add_user,
    crud_error_message,
    crud_get_user,
    crud_get_users,
    crud_delete_user,
    crud_update_user,
    crud_get_weather,
)
from api.database import engine
from api.tasks import task_add_user, task_add_weather
from api.models import UserIn, UserOut

# ---------------------------------------------------------------------
# Environment Setup
# ---------------------------------------------------------------------

# Load environment variables from parent directory (.env at project root)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

def create_db_and_tables():
    retries = 5
    for i in range(retries):
        try:
            SQLModel.metadata.create_all(engine)
            print("Database tables created.")
            break
        except OperationalError as e:
            if i == retries - 1:
                print(f"Database connection failed after {retries} attempts.")
                raise e
            print(f"Database not ready, retrying in 5 seconds... ({i+1}/{retries})")
            time.sleep(5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

# Initialize FastAPI app
app = FastAPI(lifespan=lifespan)

# Instrument Prometheus
Instrumentator().instrument(app).expose(app)

# Static frontend setup
BASE_DIR = Path(__file__).parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# ---------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------

@app.get("/")
def read_root():
    """Root endpoint for health check."""
    return {
        "service": "azure-aks-devops-pipeline",
        "owner": "M-Fahim-Feroz",
        "status": "ok"
    }


@app.get("/ui", response_class=HTMLResponse)
def serve_frontend():
    """Serve the bundled frontend (static HTML/JS/CSS)."""
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(404, crud_error_message("Frontend not found. Please build it."))
    return index_path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------
# User Endpoints
# ---------------------------------------------------------------------


@app.post("/users", response_model=UserOut)
def create_user(user: UserIn):
    """Create a new user directly."""
    db_user = crud_add_user(user)
    if db_user:
        return db_user
    raise HTTPException(400, crud_error_message("Failed to create user"))


@app.post("/users/{count}/{delay}", status_code=201)
def add_user(count: int, delay: int):
    """
    Fetch random users and insert them asynchronously using Celery.
    Redis is used as the broker, Postgres as the backend.
    """
    task = task_add_user.delay(count, delay)
    return {"task_id": task.id}


@app.post("/users/{count}", status_code=201)
def add_user_default_delay(count: int):
    """
    Same as /users/{count}/{delay} but uses a default 10s delay.
    """
    return add_user(count, 10)


@app.get("/users/{user_id}")
def get_user(user_id: int):
    """Fetch a specific user from the database."""
    user = crud_get_user(user_id)
    if user:
        return user
    raise HTTPException(404, crud_error_message(f"No user found for id: {user_id}"))


@app.get("/users", response_model=list[UserOut])
def get_users():
    """Fetch all users."""
    return crud_get_users()


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    """Delete a user by ID."""
    if crud_delete_user(user_id):
        return {"message": "User deleted successfully"}
    raise HTTPException(404, crud_error_message("User not found"))


@app.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, user: UserIn):
    """Update a user by ID."""
    updated_user = crud_update_user(user_id, user)
    if updated_user:
        return updated_user
    raise HTTPException(404, crud_error_message("User not found"))


# ---------------------------------------------------------------------
# Weather Endpoints
# ---------------------------------------------------------------------

@app.post("/weathers/{city}/{delay}", status_code=201)
def add_weather(city: str, delay: int):
    """
    Fetch weather data for a city and insert asynchronously using Celery.
    Redis is used as the broker, Postgres as the backend.
    """
    task = task_add_weather.delay(city, delay)
    return {"task_id": task.id}


@app.post("/weathers/{city}", status_code=201)
def add_weather_default_delay(city: str):
    """
    Same as /weathers/{city}/{delay} but uses a default 10s delay.
    """
    return add_weather(city, 10)


@app.get("/weathers/{city}")
def get_weather(city: str):
    """Fetch weather information from the database."""
    weather = crud_get_weather(city.lower())
    if weather:
        return weather
    raise HTTPException(404, crud_error_message(f"No weather found for city: {city}"))


# ---------------------------------------------------------------------
# Task Status Endpoint
# ---------------------------------------------------------------------

@app.get("/tasks/{task_id}")
def task_status(task_id: str):
    """
    Retrieve Celery task status.
    Possible states:
    - PENDING
    - STARTED
    - SUCCESS
    - FAILURE
    - RETRY
    - REVOKED
    """
    task = AsyncResult(task_id)
    state = task.state

    if state == "FAILURE":
        return {"state": state, "error": str(task.result)}

    return {"state": state}
