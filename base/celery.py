"""
Celery related configurations are stored into this module, by default celery catches tasks from the tasks.py module you can use
```py
from celery import shared_task
@shared_task
def your_custom_task():
    pass
```
in order to implement your own task, celery does use the app defined here for that purpose and automatically queue it in by using **rabbitmq**.

As a matter of verbosity we do use:

1. As the **Celery Backend**, django-db. This allows you to obtain the celery results from the configured django db... Maybe in order to increase performance we want to use redis or any other in memory backend? 
2. As the **Celery Broker**, rabbitmq. This is the recommended option for the queue broker of celery so we use it.
"""
import os
from logging import getLogger

from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base.settings')

logger = getLogger(__name__)

def setup_celery():
    """Configure celery and obtain the configuration from the django settings, we use a function for this in order to split responsabilities and have a little more order
    Any how this could only affect the startup time and not the overall performance."""
    app = Celery(
        "base",
        backend=f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}',
        broker_connection_retry_on_startup=True,
    )
    # Load configuration from Django settings
    app.config_from_object("django.conf:settings", namespace='CELERY')

    # Autodiscover tasks
    app.autodiscover_tasks()

    return app

app = setup_celery()
