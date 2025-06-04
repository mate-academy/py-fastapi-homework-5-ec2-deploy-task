import logging
from datetime import datetime, timezone

from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError

from database import get_sync_db_contextmanager, ActivationTokenModel
from scheduler.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task
def delete_expired_activation_tokens() -> int | None:
    with get_sync_db_contextmanager() as db:
        try:
            stmt = delete(ActivationTokenModel).where(
                ActivationTokenModel.expires_at < datetime.now(timezone.utc)
            )
            result = db.execute(stmt)
            db.commit()
            logger.info(f"Deleted tokens: {result.rowcount}")
            return result.rowcount
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error deleting tokens: {e}")
    return None
