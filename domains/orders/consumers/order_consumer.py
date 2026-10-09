import asyncio
import json

import aio_pika

from core.config import settings
from domains.orders.orders_enums import OrderEvents


async def process_order(message: aio_pika.IncomingMessage):
    async with message.process():
        event = json.loads(message.body.decode("utf-8"))

        print(f"Processing order event: {event}")

        # - iniciar o fluxo de pagamento;
        # - enviar uma notificação;
        await asyncio.sleep(60)
        print(f"Order {event['order_id']} received successfully")


async def main():
    connection = await aio_pika.connect_robust(settings.RABBITMQ_CONNECTION_URL)

    async with connection:
        channel = await connection.channel()

        await channel.set_qos(prefetch_count=1)

        exchange = await channel.declare_exchange(
            "orders",
            aio_pika.ExchangeType.DIRECT,
            durable=True,
        )

        queue = await channel.declare_queue(
            "order_processing",
            durable=True,
        )

        await queue.bind(
            exchange,
            routing_key=OrderEvents.CREATED,
        )

        await queue.consume(process_order)

        print("Waiting for order events...")

        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
