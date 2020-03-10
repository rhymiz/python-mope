![Python application](https://github.com/rhymiz/python-mope/workflows/Python%20application/badge.svg?branch=master)

# Python Mopé [under development]
Client library for Mopé by Hakrinbank

### Requirements
- Python >= 3.7,<3.8
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
