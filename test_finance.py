import pytest
from dataclasses import dataclass

from hypothesis import given, strategies
from finance import Client, Payment, OverpaymentException


@dataclass
class Case:
    id: str
    invoices: list
    payments: list
    balance: int


test_cases = [
    Case("test_invoice_alone", [100], [], 100),
    Case("test_invoice_half_paid", [100], [50], 50),
    Case("test_invoice_fully_paid", [100], [100], 0),
    Case("test_one_payment_pays_two_invoices", [100, 100], [200], 0),
    Case("test_one_invoice_payed_over_two_payments", [200], [100, 100], 0),
    Case("test_split_payment", [100, 100, 100], [150, 150], 0),
    Case("test_split_payment_with_remainder_1", [100, 100], [50, 100], 50),
    Case("test_split_payment_with_remainder_2", [200, 100, 100], [100, 200], 100),
]


@pytest.mark.parametrize("test_case", test_cases, ids=[tc.id for tc in test_cases])
def test_invoices_and_payments(test_case):
    client = Client()
    for amount in test_case.invoices:
        client.create_invoice(amount)
    for payment_amount in test_case.payments:
        client.process_payment(Payment(payment_amount))

    assert client.get_balance() == test_case.balance


def test_client_accessors():
    client = Client()
    client.create_invoice(100)

    assert len(client.get_unpaid_invoices()) == 1
    assert client.get_balance() == 100


def test_invalid_invoice_amount():
    client = Client()
    with pytest.raises(ValueError):
        client.create_invoice(0)


def test_invalid_payment_amount():
    with pytest.raises(ValueError):
        Payment(0)


def test_non_existing_invoice_base():
    client = Client()
    with pytest.raises(OverpaymentException):
        client.process_payment(Payment(100))


def test_non_existing_invoice():
    client = Client()
    client.create_invoice(100)
    client.process_payment(Payment(100))
    with pytest.raises(OverpaymentException):
        client.process_payment(Payment(100))


@strategies.composite
def invoices_and_payments(draw):
    """
    Get invoices and payments test data. Payments must always be marked against an
    invoice, so we don't generate data where there's no invoice to mark against. i.e. we
    assume that the client account can never be in credit.
    """
    invoices = draw(strategies.lists(strategies.integers(min_value=1), min_size=1))
    payments = draw(
        strategies.lists(strategies.integers(min_value=1), min_size=0).filter(
            lambda x: sum(x) <= sum(invoices)
        )
    )
    return invoices, payments


@given(invoices_and_payments())
def test_with_hypothesis(inputs):
    invoices, payments = inputs
    client = Client()
    for amount in invoices:
        client.create_invoice(amount)
    for payment_amount in payments:
        client.process_payment(Payment(payment_amount))

    assert isinstance(client.get_balance(), int)
