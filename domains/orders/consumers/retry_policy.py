import aio_pika

from domains.orders.orders_enums import OrderEvents

MAX_RETRIES = 3


async def handle_failed_message(
    message: aio_pika.IncomingMessage,
    error: Exception,
    retry_exchange: aio_pika.Exchange,
    dead_letter_exchange: aio_pika.Exchange,
) -> None:
    retry_count = int((message.headers or {}).get("x-retry-count", 0))
    print(f"Consumer callback failed (attempt {retry_count + 1}): {error}")

    if retry_count < MAX_RETRIES:
        await retry_exchange.publish(
            aio_pika.Message(
                body=message.body,
                headers={"x-retry-count": retry_count + 1},
                content_type=message.content_type,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=OrderEvents.CREATED,
        )
    else:
        await dead_letter_exchange.publish(
            aio_pika.Message(
                body=message.body,
                headers={
                    "x-retry-count": retry_count,
                    "x-error": str(error)[:500],
                },
                content_type=message.content_type,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=OrderEvents.CREATED,
        )

    await message.ack()
