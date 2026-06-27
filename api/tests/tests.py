import time
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_read_root():
    """Check that root endpoint is reachable."""
    response = client.get("/")
    assert response.status_code == 200


def wait_for_task(task_id: str, timeout: int = 30):
    """
    Poll the task state until it is SUCCESS or timeout occurs.
    Returns the final task state dictionary.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = client.get(f"/tasks/{task_id}")
        content = response.json()
        if content["state"] != "PENDING":
            return content
        time.sleep(0.5)  # Wait before polling again
    return {"state": "TIMEOUT"}


def test_task_add_user():
    """Ensure user creation task works end-to-end."""
    response = client.post("/users/1")
    assert response.status_code == 201

    task_id = response.json()["task_id"]
    assert task_id

    result = wait_for_task(task_id)
    # In CI/test mode, tasks run eagerly and complete immediately
    assert result["state"] == "SUCCESS"
    assert result["state"] != "TIMEOUT"


def test_task_add_weather():
    """Ensure weather task works end-to-end."""
    response = client.post("/weathers/erzincan")
    assert response.status_code == 201

    task_id = response.json()["task_id"]
    assert task_id

    result = wait_for_task(task_id)
    # In CI/test mode, tasks run eagerly and complete immediately
    assert result["state"] == "SUCCESS"
    assert result["state"] != "TIMEOUT"
