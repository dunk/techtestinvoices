# Overview

This set of classes models the part of a finance application that models payments and
invoices. It is assumed that invoices are raised before payments are received, and so
overpayments will be rejected. A number of cases need to be handled:

* One payment pays off one invoice
* One payment pays off multiple invoices
* Multiple payments pay off one invoice

Given the combination of these factors, the classes have been built to account for
edge-cases like a payment paying off one whole invoice, and then part of another.

# Notes, Caveats, and Extensions

In reality we would be using a relational database to model these items, with an ORM in
between. Classes would have ids, etc, and `PaymentInvoice` would be a join table.

Given that we would be using a database, `get_balance` would be implemented via queries,
rather than a series of loops.

Additionally, we would use the transactional nature of the database to revert a series
of updates to payments that result in an error (chiefly at the moment, the `OverpaymentException`). As the code stands it will make an unsafe series of edits that can't be reverted. In code this code be addressed by modeling the series of edits as events, and then later applying this series once we know it's safe.

# Tests

To execute the test suite run `pytest test_finance.py`

`pytest` has been used as it is quite powerful. A series of test cases have been set up
via a custom dataclass so as to keep the self-documenting ids alongside the test cases
that they refer to, while still being able to use `pytest.mark.parametrize`. This can
also be done with the more expansive `pytest-cases` library.

Hypothesis has been used in order to make the tests more robust.
