Write-Host "Installing uv..."
pip install uv

Write-Host "Installing dependencies..."
uv sync --no-dev

Write-Host "Running internal migrations..."
uv run python master_data/manage.py makemigrations

Write-Host "Running database migrations..."
uv run python master_data/manage.py migrate master --database=master
uv run python master_data/manage.py migrate sales --database=sales
uv run python master_data/manage.py migrate

Write-Host "Collect static files..."
uv run python master_data/manage.py collectstatic

Write-Host "Running server.."
uv run python master_data/manage.py runserver