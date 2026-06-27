Write-Host "Running Azure AKS Preflight Checks..."
python -m compileall api
$env:DATABASE_URL="sqlite:///test.db"
$env:CELERY_BROKER_URL="memory://"
$env:CELERY_RESULT_BACKEND="cache+memory://"
$env:WEATHER_API_KEY="test-key"
$env:CELERY_TASK_ALWAYS_EAGER="True"
pytest api/tests/ -v --tb=short
flake8 api/ --count --select=E9,F63,F7,F82 --show-source --statistics
bandit -r api/ -lll --exclude api/tests/

