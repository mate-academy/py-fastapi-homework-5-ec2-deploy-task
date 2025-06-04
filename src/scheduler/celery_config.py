from urllib.parse import urlparse

from celery.schedules import crontab

from config import get_settings

settings = get_settings()


class RedisCeleryConfig:
    def __init__(self):
        self.broker_url = settings.CELERY_BROKER_URL
        self.result_backend = settings.CELERY_RESULT_BACKEND
        self._validate_redis_urls()

    def _validate_redis_urls(self) -> None:
        for url in [self.broker_url, self.result_backend]:
            parsed = urlparse(url)
            if parsed.scheme != "redis":
                raise ValueError(f"Invalid Redis URL scheme: {url}")

    def get_settings(self) -> dict:
        return {
            "broker_url": self.broker_url,
            "result_backend": self.result_backend,
            "task_serializer": "json",
            "result_serializer": "json",
            "accept_content": ["json"],
            "timezone": "Europe/Kiev",
            "enable_utc": True,
            "task_track_started": True,
            "task_time_limit": 30 * 60,
            "task_soft_time_limit": 25 * 60,
            "worker_prefetch_multiplier": 1,
            "worker_max_tasks_per_child": 1000,
            "worker_max_memory_per_child": 150000,
            "result_expires": 60 * 60 * 24,
            "result_backend_max_retries": 3,
            "beat_schedule": {
                "delete-expired-activation-tokens": {
                    "task": "scheduler.tasks.delete_expired_activation_tokens",
                    "schedule": crontab()
                },
            },
        }
