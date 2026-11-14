![build](https://github.com/rhymiz/python-mope/workflows/build/badge.svg)
[![downloads](https://pepy.tech/badge/python-mope)](https://pepy.tech/project/python-mope)
[![Ruff](https://img.shields.io/badge/lint%20and%20format-Ruff-D7FF64.svg)](https://docs.astral.sh/ruff/)

# Python Mopé
Client library for Mopé by Hakrinbank

### Token acquisition and API Docs
- [API Docs](https://api.mope.sr/integration/doc)
- Instructions for [acquiring a token](https://drive.google.com/file/d/10fWqgpl2Ip9JIacl0pwzUDi_HV6WLbCi/view?usp=sharing)


### Requirements
- Python 3.11 or newer
- Mopé API Token

### Getting Started
First, install from PyPi by running `pip install python-mope`

Example usage:

```python
from mope import Mope

mope = Mope(token="test_123")
mope.shop.get_payment_request(payment_id="123")
```

### Development

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run:

```sh
uv sync --locked
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked ty check
uv run --locked pytest
uv build --no-sources
```

Development uses Python 3.15.2 from `.python-version`; uv installs it when needed.
The library supports Python 3.11+, and CI tests the built wheel on Python 3.11,
3.12, 3.13, 3.14, and 3.15. Ruff and ty target Python 3.11 compatibility.
Run `uv run ruff format .` to format code. Commit `uv.lock` after changing
dependencies; use `uv lock --upgrade` to refresh their locked versions.

The package includes inline types and a `py.typed` marker. API responses are
validated before creating models: invalid field types raise `TypeError`, invalid
status values raise `ValueError`, and missing required fields raise `KeyError`.
Values are not coerced. Payment metadata remains a list of dictionaries with
string `key` and `value` fields, as defined by the
[Mopé API schema](https://api.mope.sr/integration/paths/GetPaymentRequest.yaml).

### Publishing

To release, update `mope/__version__.py`, run `uv lock`, and commit the changes.
Publish a GitHub release whose tag is the package version or `v` followed by that
version. The workflow checks the tag, runs lint, formatting and type checks,
builds the source distribution and wheel, and tests the installed wheel across
all supported Python versions before uploading those same artifacts to PyPI.

### Resources
#### shop

*Methods*

##### `shop.create_payment_request`

| Argument   | Type                | Required |
| ---        |---                  | ---      |
|amount      | int                 | yes      |
|description | string              | yes      |
|order_id    | string              | yes      |
|currency    | enum (USD, SRD, EUR) | yes      |
|redirect_url| string              | yes      |


return type: `mope.models.payments.CreatePaymentResponse`

##### `shop.get_payment_request`

| Argument  | Type   | Required |
|---        |---     |---       |
|payment_id | string | yes      |


return type: `mope.models.payments.PaymentRequest`
