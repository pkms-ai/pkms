import logging

from universal_worker.exceptions import ContentProcessingError
from universal_worker.models import Content
from universal_worker.config import settings
import httpx

logger = logging.getLogger(__name__)


def build_response_message(content: Content) -> str:
    # if content.error:
    #     return f"Content has failed with error: {content.error}"
    # return f"Content has been {content.status.value} successfully."
    return "under construction"


async def simple_notytify(content: Content) -> None:
    logger.info(build_response_message(content))


async def notify_telegram(content: Content) -> None:
    if content.source is None or content.source.telegram is None:
        # should not be here but just in case
        logger.info(
            f"Content source or Telegram source is not available for content: {content.url}"
        )
        return

    telegram_source = content.source.telegram

    logger.info(f"Sending notification to Telegram for content: {content.url}")
    # Send notification to Telegram
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"

    response_message = build_response_message(content)
    payload = {
        "chat_id": telegram_source.chat_id,
        "reply_to_message_id": telegram_source.message_id,
        "text": response_message,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                logger.info(f"Notification sent to Telegram for content: {content.url}")
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


async def notify(content: Content) -> None:
    """Notify the user about the content."""
    try:
        if content.source is None:
            logger.info(f"Content source is not available for content: {content}")
            return

        logger.info(f"Sending notification for content: {content}")
        # Send notification to the user
        # Dynamically find the key in ContentSource that has data
        found = False
        for key, notifier in notifiers.items():
            source_data = getattr(content.source, key, None)
            if source_data is not None:
                await notifier(content)
                logger.info(f"Notification sent for content: {content}")
                found = True

        if not found:
            await simple_notytify(content)
            logger.info(f"No valid notifier found for content source: {content.source}")
    except Exception as e:
        logger.error(f"Error sending notification for content: {content}: {e}")
        raise ContentProcessingError(
            f"Error sending notification for content: {content}: {e}"
        )
