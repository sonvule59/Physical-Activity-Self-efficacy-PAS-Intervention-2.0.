# # web: gunicorn config.wsgi --log-file - 
# web: gunicorn --chdir testpas testpas.wsgi
# web: gunicorn testpas:app
# web: gunicorn config.wsgi
web: gunicorn config.wsgi --log-file -
release: python manage.py migrate