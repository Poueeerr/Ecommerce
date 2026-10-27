import asyncio
import uuid

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from domains.orders.orders_enums import OrderStatus
from domains.orders.repositories.orders_repository import OrdersRepository
from domains.orders.schemas.event_schema import OrderCreatedEvent

from domains.payments.adapters.mercadopago import MercadoPagoAdapter
from domains.payments.models.payments_model import PaymentsModel
from domains.payments.payments_enums import PaymentsStatus
from domains.payments.repositories.payments_repository import PaymentsRepository


class PaymentsService:
    def __init__(
        self,
        session: AsyncSession,
        payments_repository: PaymentsRepository,
        orders_repository: OrdersRepository,
        payment_adapter: MercadoPagoAdapter | None = None,
    ):
        self.session = session
        self.payments_repository = payments_repository
        self.orders_repository = orders_repository
        self.payment_adapter = payment_adapter

    async def create_provider_payment(
        self,
        event: OrderCreatedEvent,
    ) -> dict:
        if self.payment_adapter is None:
            raise RuntimeError(
                "Adapter de pagamento não configurado"
            )

        # Busca e valida o pagamento antes da chamada externa.
        async with self.session.begin():
            payment = await self.payments_repository.get_by_order_id(
                event.order_id,
                lock=True,
            )

            if payment is None:
                raise ValueError(
                    f"Pagamento não encontrado para o pedido {event.order_id}"
                )

            if payment.total != event.total:
                raise ValueError(
                    "Valor do evento diverge do pagamento registrado"
                )

            if payment.provider_preference_id:
                return {
                    "provider_preference_id": payment.provider_preference_id,
                    "checkout_url": payment.checkout_url,
                }

            if payment.status != PaymentsStatus.PENDING:
                raise ValueError(
                    "Não é possível criar checkout para esse status"
                )

            if payment.provider not in (None, "mercado_pago"):
                raise ValueError(
                    "Provedor de pagamento divergente"
                )

            amount = payment.total
            email = event.email
            order_id = str(event.order_id)

        # A chamada externa ocorre fora da transação do banco.
        provider_payment = await asyncio.to_thread(
            self.payment_adapter.create_payment,
            order_id=order_id,
            amount=amount,
            email=email,
        )

        # Salva o resultado em uma nova transação.
        async with self.session.begin():
            payment = await self.payments_repository.get_by_order_id(
                event.order_id,
                lock=True,
            )

            if payment is None:
                raise ValueError(
                    f"Pagamento não encontrado para o pedido {event.order_id}"
                )

            # Outra execução pode ter criado a preferência enquanto
            # a chamada externa estava em andamento.
            if payment.provider_preference_id:
                return {
                    "provider_preference_id": payment.provider_preference_id,
                    "checkout_url": payment.checkout_url,
                }

            if payment.status != PaymentsStatus.PENDING:
                raise ValueError(
                    "O status do pagamento mudou durante a criação do checkout"
                )

            payment.provider = "mercado_pago"
            payment.provider_preference_id = (
                provider_payment["provider_preference_id"]
            )
            payment.checkout_url = provider_payment["checkout_url"]

            return provider_payment

    async def process_webhook(
        self,
        notification: dict,
    ) -> None:
        if self.payment_adapter is None:
            raise RuntimeError(
                "Adapter de pagamento não configurado"
            )

        if notification.get("type") != "payment":
            return

        data = notification.get("data") or {}
        raw_payment_id = data.get("id")

        if raw_payment_id is None:
            raise ValueError(
                "Notificação sem ID do pagamento"
            )

        payment_id = str(raw_payment_id)

        # Não confiar no status enviado pelo webhook.
        # Consultar o estado real do pagamento no provedor.
        provider_payment = await asyncio.to_thread(
            self.payment_adapter.get_payment,
            payment_id,
        )

        if str(provider_payment.get("id")) != payment_id:
            raise ValueError(
                "ID do pagamento divergente"
            )

        external_reference = provider_payment.get(
            "external_reference"
        )

        if not external_reference:
            raise ValueError(
                "Pagamento sem referência do pedido"
            )

        try:
            order_id = uuid.UUID(str(external_reference))
        except (ValueError, TypeError, AttributeError) as exc:
            raise ValueError(
                "Referência do pedido inválida"
            ) from exc

        try:
            provider_amount = Decimal(
                str(provider_payment["transaction_amount"])
            )
        except (KeyError, ValueError, TypeError) as exc:
            raise ValueError(
                "Valor do pagamento inválido"
            ) from exc

        if provider_payment.get("currency_id") != "BRL":
            raise ValueError(
                "Moeda do pagamento divergente"
            )

        status_mapping = {
            "approved": PaymentsStatus.APPROVED,
            "pending": PaymentsStatus.PENDING,
            "in_process": PaymentsStatus.IN_PROCESS,
            "authorized": PaymentsStatus.AUTHORIZED,
            "in_mediation": PaymentsStatus.IN_MEDIATION,
            "rejected": PaymentsStatus.REJECTED,
            "cancelled": PaymentsStatus.CANCELLED,
            "refunded": PaymentsStatus.REFUNDED,
            "charged_back": PaymentsStatus.CHARGED_BACK,
        }

        provider_status = provider_payment.get("status")
        new_status = status_mapping.get(provider_status)

        if new_status is None:
            raise ValueError(
                f"Status de pagamento não mapeado: {provider_status}"
            )

        async with self.session.begin():
            payment = await self.payments_repository.get_by_order_id(
                order_id,
                lock=True,
            )

            if payment is None:
                raise ValueError(
                    f"Pagamento não encontrado para o pedido {order_id}"
                )

            order = await self.orders_repository.get_by_id(
                order_id,
                lock=True,
            )

            if order is None:
                raise ValueError(
                    f"Pedido não encontrado: {order_id}"
                )

            if payment.provider not in (None, "mercado_pago"):
                raise ValueError(
                    "Provedor de pagamento divergente"
                )

            if payment.total != provider_amount:
                raise ValueError(
                    "Valor do pagamento divergente"
                )

            if Decimal(str(order.total)) != provider_amount:
                raise ValueError(
                    "Valor do pedido divergente"
                )

            existing_payment = (
                await self.payments_repository.get_by_provider_payment_id(
                    payment_id
                )
            )

            if (
                existing_payment is not None
                and existing_payment.id != payment.id
            ):
                raise ValueError(
                    "Pagamento já associado a outro registro"
                )

            current_status = payment.status

            # Eventos repetidos não devem desfazer uma aprovação.
            if current_status == PaymentsStatus.APPROVED:
                if new_status in (
                    PaymentsStatus.PENDING,
                    PaymentsStatus.IN_PROCESS,
                    PaymentsStatus.AUTHORIZED,
                ):
                    return

                if new_status in (
                    PaymentsStatus.REJECTED,
                    PaymentsStatus.CANCELLED,
                ):
                    return

            if (
                new_status == PaymentsStatus.APPROVED
                and order.status == OrderStatus.CANCELED
            ):
                raise ValueError(
                    "Não é possível aprovar o pagamento de um pedido cancelado"
                )

            payment.provider = "mercado_pago"
            payment.provider_payment_id = payment_id
            payment.status = new_status

            if new_status == PaymentsStatus.APPROVED:
                if order.status == OrderStatus.PAYMENT_PENDING:
                    order.status = OrderStatus.PROCESSING

            elif new_status in (
                PaymentsStatus.CANCELLED,
                PaymentsStatus.REJECTED,
            ):
                if order.status == OrderStatus.PAYMENT_PENDING:
                    order.status = OrderStatus.CANCELED

    async def update_from_provider(
        self,
        order_id: uuid.UUID,
        provider_payment_id: str,
        status: PaymentsStatus = PaymentsStatus.PENDING,
    ) -> PaymentsModel:
        """
        Atualização interna de compatibilidade.

        Para notificações do Mercado Pago, utilize process_webhook(),
        que consulta o provedor e valida os dados.
        """
        async with self.session.begin():
            payment = await self.payments_repository.get_by_order_id(
                order_id,
                lock=True,
            )

            if payment is None:
                raise ValueError(
                    f"Pagamento não encontrado para o pedido {order_id}"
                )

            existing_payment = (
                await self.payments_repository.get_by_provider_payment_id(
                    provider_payment_id
                )
            )

            if (
                existing_payment is not None
                and existing_payment.id != payment.id
            ):
                raise ValueError(
                    "Pagamento já associado a outro registro"
                )

            payment.provider_payment_id = provider_payment_id
            payment.status = status

            return payment

    async def get_checkout(
        self,
        order_id: uuid.UUID,
    ) -> PaymentsModel:
        payment = await self.payments_repository.get_by_order_id(
            order_id
        )

        if payment is None:
            raise ValueError(
                f"Pagamento não encontrado para o pedido {order_id}"
            )

        return payment