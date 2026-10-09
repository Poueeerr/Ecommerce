from collections.abc import AsyncIterator

import aio_pika

from core.config import settings
from domains.orders.events.order_publisher import OrderPublisher


async def get_order_publisher() -> AsyncIterator[OrderPublisher]:
    connection = await aio_pika.connect_robust(settings.RABBITMQ_CONNECTION_URL)
    try:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            "orders",
            aio_pika.ExchangeType.DIRECT,
            durable=True,
        )
        yield OrderPublisher(exchange)
    finally:
        await connection.close()
