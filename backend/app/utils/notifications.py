import logging

logger = logging.getLogger(__name__)

def send_notification(to_user_id: int, message: str) -> None:
    """Placeholder notification sender.

    In a real system this could send an email, SMS, or push notification.
    For now it logs the message for debugging purposes.
    """
    logger.info(f"Notification to user {to_user_id}: {message}")
