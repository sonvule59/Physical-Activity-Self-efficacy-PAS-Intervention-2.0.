# # web: gunicorn config.wsgi --log-file - 
# web: gunicorn --chdir testpas testpas.wsgi
web: gunicorn testPAS:app
# web: gunicorn config.wsgi
web: gunicorn config.wsgi --log-file -
release: python manage.py migrate
worker: celery worker --app=tasks.app