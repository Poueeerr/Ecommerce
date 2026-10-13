from uuid import uuid4

from domains.payments.schemas.payments_schema import PaymentsSchema


class PaymentFactory:
    @staticmethod
    def build_schema(**overrides) -> PaymentsSchema:
        values = {"id": uuid4()}
        values.update(overrides)
        return PaymentsSchema(**values)

    @staticmethod
    def build_webhook(**overrides) -> dict[str, str]:
        values = {"provider_payment_id": "provider-payment-id"}
        values.update(overrides)
        return values
