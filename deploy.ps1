Write-Host "Installing pipenv..."
pip install pipenv

Write-Host "Installing dependencies..."
pipenv install

Write-Host "Activating virtual environment..."
pipenv shell

Write-Host "Running database migrations..."
py master_data/manage.py migrate
py master_data/manage.py migrate master --database=master

Write-Host "Collect static files..."
py master_data/manage.py collectstatic

Write-Host "Running server..."
py master_data/manage.py runserver