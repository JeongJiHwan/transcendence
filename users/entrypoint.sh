# Install dependencies
python -m venv venv

source venv/bin/activate

pip install pip==21.0.1
pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate

python manage.py runserver 0.0.0.0:8000