# from __future__ import absolute_import, unicode_literals
# import os
# from celery import Celery
from testpas import settings
import django
# from celery.schedules import crontab

# # Set the default Django settings module for the 'celery' program
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpas.settings')

# app = Celery('testpas')

# # Using a string here means the worker doesn't have to serialize
# # the configuration object to child processes.
# app.config_from_object('django.conf:settings', namespace='CELERY')

# # Load task modules from all registered Django app configs.
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# app.conf.beat_schedule = {
#     'run-randomization': {
#         'task': 'your_app.tasks.run_randomization',
#         'schedule': crontab(hour=0, minute=1, day_of_month=31),
#     },
# }

# @app.task(bind=True)
# def debug_task(self):
#     print(f'Request: {self.request!r}')
# config/celery.py
import os
from celery import Celery

# Set the default Django settings module for Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpas.settings')

# Create Celery app instance
app = Celery('config')
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

# Load configuration from Django settings (e.g., CELERY_BROKER_URL)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in installed apps (e.g., testpas.tasks)
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS, related_name='tasks')