# Install dependencies
echo "Installing dependencies..."
pipenv run install -r requirements.txt

# Activate virtual environment
echo "Activating virtual environment..."
pipenv shell

# Run migrations
echo "Running internal migrations..."
pipenv run python master_data/manage.py makemigrations

# Run migrations
echo "Running migrations..."
pipenv run python master_data/manage.py migrate master --database=master
pipenv run python master_data/manage.py migrate sales --database=sales
pipenv run python master_data/manage.py migrate

# Collect static files
echo "Collecting static files..."
pipenv run python master_data/manage.py collectstatic

# Run Django server (this step might be omitted on production)
echo "Starting Django server..."
pipenv run python master_data/manage.py runserver
