# rag_app/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rag_app.settings')
app = Celery('rag_app')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
