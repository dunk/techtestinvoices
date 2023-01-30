class Client:
    def __init__(self):
        self.invoices = []

    def create_invoice(self, amount):
        """
        Create an invoice for this client
        """
        self.invoices.append(Invoice(amount))

    def get_balance(self):
        """
        Get the outstanding balance across all invoices
        """
        # NOTE caching / db query would be done here
        invoiced_total = 0
        payed_total = 0
        for invoice in self.invoices:
            invoiced_total += invoice.amount
            for pi in invoice.payment_invoices:
                payed_total += pi.amount
        return invoiced_total - payed_total

    def get_unpaid_invoices(self):
        """
        Get all unpaid invoices for this client

        We pay invoices in the order that they were created
        """
        return [i for i in self.invoices if not i.is_paid()]

    def process_payment(self, payment):
        """
        Apply a payment to one or more invoices

        We retrieve all unpaid invoices, and iteratively apply the payment to them until
        there is no more money to assign. The last invoice visited may end up
        part-paid or fully-paid, depending on the amount remaining.

        If the incoming payment exceeds the outstanding invoices, then we return an
        exception
        """
        # NOTE: not transactional
        invoices = self.get_unpaid_invoices()

        invoices = iter(self.get_unpaid_invoices())
        remaining = payment.amount
        while True:
            try:
                invoice = next(invoices)
            except StopIteration:
                raise OverpaymentException()
            remaining = invoice.apply_payment(payment, remaining)
            if remaining == 0:
                break


class OverpaymentException(Exception):
    """
    Exception raised when an incoming payment doesn't match the set of outstanding
    invoices
    """
    pass


class PaymentInvoice:
    """
    Connects payments to invoices, storing the amount the payment contributes towards
    the invoice
    """
    def __init__(self, payment, invoice, amount):
        self.payment = payment
        self.invoice = invoice
        self.amount = amount


class Invoice:
    def __init__(self, amount):
        if amount <= 0:
            raise ValueError("Invoices must have a positive value")
        self.amount = amount
        self.payment_invoices = []

    def add_payment_invoice(self, payment_invoice):
        self.payment_invoices.append(payment_invoice)

    def is_paid(self):
        """
        Check whether this invoice has been fully paid
        """
        return self.amount_paid() == self.amount

    def amount_paid(self):
        """
        Get the amount that has been paid off of this invoice so far
        """
        return sum(pi.amount for pi in self.payment_invoices)

    def outstanding_amount(self):
        """
        Get the remaining amount that is still to be paid on this invoice
        """
        return self.amount - self.amount_paid()

    def apply_payment(self, payment, remaining):
        """
        Apply a payment to this invoice, returning the remaining payment amount
        """
        outstanding = self.outstanding_amount()
        contribution = outstanding if remaining >= outstanding else remaining
        self.add_payment_invoice(PaymentInvoice(payment, self, contribution))
        return remaining - contribution


class Payment:
    """
    Represents an incoming payment, towards one or more invoices
    """
    def __init__(self, amount):
        if amount <= 0:
            raise ValueError("Payments must have a positive value")
        self.amount = amount
        self.payment_invoices = []

    def add_payment_invoice(self, payment_invoice):
        self.payment_invoices.append(payment_invoice)
