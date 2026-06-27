import os
import time
import requests
from celery import Celery
from api.crud import crud_add_user, crud_add_weather
from api.models import UserIn, WeatherIn


# ---------------------------------------------------------------------
# Environment-Aware Setup
# ---------------------------------------------------------------------

# Detect test / CI environment
IS_CI = os.getenv("GITHUB_ACTIONS") == "true"
IS_TEST = "pytest" in os.getenv("PYTEST_CURRENT_TEST", "")

# Force in-memory eager backend in CI or tests (ensures consistent task results)
if IS_CI or IS_TEST:
    os.environ["CELERY_RESULT_BACKEND"] = "cache+memory://"
    os.environ["CELERY_TASK_ALWAYS_EAGER"] = "True"
    os.environ["CELERY_TASK_STORE_EAGER_RESULT"] = "True"

# Get URLs from environment variables
REDIS_URL = os.getenv("CELERY_BROKER_URL")
DATABASE_URL = os.getenv("DATABASE_URL")
# Weather API key (must be provided via environment)
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

if not REDIS_URL:
    raise ValueError("CELERY_BROKER_URL environment variable is not set")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Pick backend depending on environment
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", DATABASE_URL)

# Initialize Celery
app = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=RESULT_BACKEND,
)

# Base Celery config
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Activate eager mode explicitly if flagged
if os.getenv("CELERY_TASK_ALWAYS_EAGER") == "True":
    app.conf.update(
        task_always_eager=True,
        task_store_eager_result=True,
    )


# ---------------------------------------------------------------------
# Celery Tasks
# ---------------------------------------------------------------------


@app.task
def task_add_user(count: int, delay: int):
    """Fetch random user data and add them to the database."""
    url = "https://randomuser.me/api"
    try:
        response = requests.get(f"{url}?results={count}", timeout=10)
        response.raise_for_status()
        data = response.json()["results"]
    except Exception as e:
        return {"error": f"Failed to fetch user data: {e}"}

    time.sleep(delay)
    result = []

    for item in data:
        user = UserIn(
            first_name=item["name"]["first"],
            last_name=item["name"]["last"],
            mail=item["email"],
            age=item["dob"]["age"],
        )
        if crud_add_user(user):
            result.append(user.dict())

    return {"success": result, "inserted": len(result)}


@app.task
def task_add_weather(city: str, delay: int):
    """Fetch weather data for the specified city and insert into database."""
    url = f"https://api.collectapi.com/weather/getWeather?data.lang=tr&data.city={city}"
    if not WEATHER_API_KEY:
        # Fail fast so developers/CI know the key must be set
        raise ValueError("WEATHER_API_KEY environment variable is not set")

    headers = {
        "content-type": "application/json",
        # "authorization": "apikey 4HKS8SXTYAsGz45l4yIo9P:0NVczbcuJfjQb8PW7hQV48",
        "authorization": f"apikey {WEATHER_API_KEY}",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()["result"]
    except Exception as e:
        return {"error": f"Failed to fetch weather data: {e}"}

    time.sleep(delay)
    result = []

    for item in data:
        weather = WeatherIn(
            city=city.lower(),
            date=item["date"],
            day=item["day"],
            description=item["description"],
            degree=item["degree"],
        )
        if crud_add_weather(weather):
            result.append(weather.dict())

    return {"success": result, "inserted": len(result)}
