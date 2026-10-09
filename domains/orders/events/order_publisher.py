import json

import aio_pika

from domains.orders.events.order_created import OrderCreatedEvent
from domains.orders.orders_enums import OrderEvents


class OrderPublisher:
    def __init__(self, exchange):
        self.exchange = exchange

    async def publish_order_created(
            self,
            event: OrderCreatedEvent
    ):
        message = aio_pika.Message(
            body=json.dumps(
                event.model_dump(mode="json")
            ).encode("utf-8"),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        await self.exchange.publish(
            message,
            routing_key=OrderEvents.CREATED
        )
