import json
import re

import aio_pika

from .config import settings


async def publish_to_queue(queue_name: str, message: dict):
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        await channel.declare_queue(queue_name, durable=True)

        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=queue_name,
        )


def extract_url(content: str) -> str | None:
    # Simple regex to extract URLs
    url_pattern = re.compile(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    )
    urls = url_pattern.findall(content)

    if urls:
        return urls[0]
    return None


def contains_url(text: str) -> bool:
    # Regular expression pattern for URLs
    url_pattern = re.compile(r"(https?://\S+|www\.\S+)", re.IGNORECASE)
    # Search for the pattern in the text

    return bool(url_pattern.search(text))
