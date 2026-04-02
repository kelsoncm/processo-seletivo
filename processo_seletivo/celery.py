import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'processo_seletivo.settings')

app = Celery('processo_seletivo')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
