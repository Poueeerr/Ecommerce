from domains.payments.payments_enums import PaymentsStatus
from domains.payments.payments_exceptions import PaymentNotFound
from tests.domains.payments.factories import PaymentFactory


def test_payment_schema_accepts_payment_id():
    payment = PaymentFactory.build_schema()

    assert payment.id is not None


def test_payment_status_contains_pending_and_approved():
    assert PaymentsStatus.PENDING.value == "pending"
    assert PaymentsStatus.APPROVED.value == "approved"


def test_payment_not_found_is_not_found_error():
    error = PaymentNotFound()

    assert error.status_code == 404
