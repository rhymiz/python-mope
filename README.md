![build](https://github.com/rhymiz/python-mope/workflows/build/badge.svg)
[![downloads](https://pepy.tech/badge/python-mope)](https://pepy.tech/project/python-mope)

# Python Mopé
Client library for Mopé by Hakrinbank

### Token acquisition and API Docs
- [API Docs](https://api.mope.sr/integration/doc)
- Instructions for [acquiring a token](https://drive.google.com/file/d/10fWqgpl2Ip9JIacl0pwzUDi_HV6WLbCi/view?usp=sharing)


### Requirements
- Python >= 3.6,<=3.10
- requests (currently not sure what the min required version is)
- Mopé API Tokens

### Getting Started
First, you can install from PyPi by running `pip install python-mope`

Example usage:

```python
from mope import Mope

mope = Mope(token='test_123')
mope.shop.get_payment_request(payment_id='123')
```

### Resources
#### shop

*Methods*

##### `shop.create_payment_request`

| Argument   | Type                | Required |
| ---        |---                  | ---      |
|amount      | int                 | yes      |
|description | string              | yes      |
|order_id    | string              | yes      |
|currency    | enum (USD, SRD, EU) | yes      | 
|redirect_url| string              | yes      |


return type: `mope.models.payments.CreatePaymentResponse`

##### `shop.get_payment_request`

| Argument  | Type   | Required |
|---        |---     |---       |
|payment_id | string | yes      |


return type: `mope.models.payments.PaymentRequest`
