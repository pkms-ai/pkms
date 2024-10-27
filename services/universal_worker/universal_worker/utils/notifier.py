import aio_pika
from aio_pika import DeliveryMode, Message

from universal_worker.config import settings
from universal_worker.models import NotificationMessage


async def notify(notification_message: NotificationMessage) -> None:
    # Establish connection
    connection = await aio_pika.connect_robust(
        settings.RABBITMQ_URL
    )  # Update with your RabbitMQ credentials

    async with connection:
        # Open a channel
        channel = await connection.channel()

        # Declare the queue
        queue = await channel.declare_queue(settings.NOTIFY_QUEUE, durable=True)

        # Prepare the message content
        message_body = (
            notification_message.model_dump_json()
        )  # Serialize NotificationMessage to JSON

        # Publish message to the queue
        await channel.default_exchange.publish(
            Message(
                body=message_body.encode(),
                delivery_mode=DeliveryMode.PERSISTENT,  # Makes the message persistent
            ),
            routing_key=queue.name,
        )
