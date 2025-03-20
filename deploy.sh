pipenv install

pipenv shell

pipenv run py master_data/manage.py makemigrations

pipenv run py master_data/manage.py migrate master --database=master
pipenv run py master_data/manage.py migrate sales --database=sales
pipenv run py master_data/manage.py migrate

pipenv run py master_data/manage.py collectstatic

pipenv run py master_data/manage.py runserver