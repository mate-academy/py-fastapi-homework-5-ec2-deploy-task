from celery import Celery

from scheduler.celery_config import RedisCeleryConfig

config = RedisCeleryConfig()
celery_app = Celery("scheduler")
celery_app.conf.update(config.get_settings())

celery_app.autodiscover_tasks()
