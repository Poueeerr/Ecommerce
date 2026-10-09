from uuid import uuid4

from domains.payments.payments_enums import PaymentsStatus
from domains.payments.payments_exceptions import PaymentNotFound
from domains.payments.schemas.payments_schema import PaymentsSchema


def test_payment_schema_accepts_payment_id():
    payment_id = uuid4()

    payment = PaymentsSchema(id=payment_id)

    assert payment.id == payment_id


def test_payment_status_contains_pending_and_approved():
    assert PaymentsStatus.PENDING.value == "pending"
    assert PaymentsStatus.APPROVED.value == "approved"


def test_payment_not_found_is_not_found_error():
    error = PaymentNotFound()

    assert error.status_code == 404
