web: gunicorn testpas.wsgi --log-file - 
release: python manage.py migrate
web: gunicorn --chdir testpas testpas.wsgi
web: gunicorn testpas:app
