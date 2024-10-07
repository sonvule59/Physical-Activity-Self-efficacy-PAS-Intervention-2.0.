 web gunicorn testpas.wsgi --log-file - 
release: python manage.py migrate
web: gunicorn config.wsgi --log-file - --log-level debug
web: gunicorn testpas:app
