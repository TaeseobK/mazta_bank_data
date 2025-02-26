Write-Host "Installing pipenv..."
pip install pipenv

Write-Host "Installing dependencies..."
pipenv install

Write-Host "Activating virtual environment..."
pipenv shell

Write-Host "Running database migrations..."
pipenv run py master_data/manage.py migrate
pipenv run py master_data/manage.py migrate master --database=master

Write-Host "Collect static files..."
pipenv run py master_data/manage.py collectstatic

Write-Host "Running server..."
pipenv run py master_data/manage.py runserver