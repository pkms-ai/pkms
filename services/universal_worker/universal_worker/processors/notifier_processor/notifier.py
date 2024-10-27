import logging

from universal_worker.exceptions import ContentProcessingError
from universal_worker.models import NotificationMessage
from universal_worker.config import settings
import httpx

logger = logging.getLogger(__name__)


def build_response_message(message: NotificationMessage) -> str:
    if message.message:
        return message.message
    return f"Content has been {message.status.value} successfully"


async def simple_notytify(message: NotificationMessage) -> None:
    logger.info(build_response_message(message))


async def notify_telegram(message: NotificationMessage) -> None:
    if message.source is None or message.source.telegram is None:
        # should not be here but just in case
        logger.info(
            f"Content source or Telegram source is not available for content: {message.url}"
        )
        await simple_notytify(message)
        return

    telegram_source = message.source.telegram

    logger.info(f"Sending notification to Telegram for content: {message.url}")
    # Send notification to Telegram
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"

    response_message = build_response_message(message)
    payload = {
        "chat_id": telegram_source.chat_id,
        "reply_to_message_id": telegram_source.message_id,
        "text": response_message,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                logger.info(f"Notification sent to Telegram for content: {message.url}")
            else:
                logger.error(
                    f"Failed to send notification to Telegram. Status: {response.status_code}, Error: {response.text}"
                )
        except httpx.RequestError as e:
            logger.error(
                f"An error occurred while sending notification to Telegram: {e}"
            )


notifiers = {
    "telegram": notify_telegram,
}


async def notify(message: NotificationMessage) -> None:
    """Notify the user about the content."""
    try:
        if message.source is None:
            logger.info(f"Content source is not available for content: {message.url}")
            await simple_notytify(message)
            return

        logger.info(f"Sending notification for content: {message.url}")
        # Send notification to the user
        # Dynamically find the key in ContentSource that has data
        found = False
        for key, notifier in notifiers.items():
            source_data = getattr(message.source, key, None)
            if source_data is not None:
                await notifier(message)
                logger.info(f"Notification sent for content: {message.url}")
                found = True

        if not found:
            await simple_notytify(message)
            logger.info(f"No valid notifier found for content: {message.url}")
    except Exception as e:
        logger.error(f"Error sending notification for content: {message.url}: {e}")
        raise ContentProcessingError(
            f"Error sending notification for content: {message.url}: {e}"
        )
