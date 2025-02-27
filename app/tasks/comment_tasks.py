# app/tasks/comment_tasks.py
from app.core.celery_utils import celery
from app.utils.instagram_api import sendreply, get_access_token_for_account
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

@celery.task(name="send_delayed_reply")
def send_delayed_reply(comment_id, message_to_be_sent, account_id_to_use):
    """Sends a delayed reply to a comment."""
    try:
        access_token_to_use = get_access_token_for_account(account_id_to_use)
        result = sendreply(access_token_to_use, comment_id, message_to_be_sent)
        logger.info(f"Reply sent to comment {comment_id} using account {account_id_to_use}. Result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error sending reply to comment {comment_id} using account {account_id_to_use}: {e}")
        raise  # Re-raise for Celery retry