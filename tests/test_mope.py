import unittest
from unittest import mock
from unittest.mock import Mock

from mope import Mope
from mope.models.payments import Currency, PaymentRequest

mock_payment_request = {
    'id': 'c43f24a3-df4f-43b7-9045-b454529369dc',
    'amount': 35638,
    'created_at': '2019-12-02T14:28:14+00:00',
    'description': 'Order for a lot of beer',
    'expires_at': '2019-12-03T14:28:14+00:00',

    'currency': {
        'name': 'Surinamese dollar',
        'code': 'SRD',
        'symbol': '$'
    },
    'status': 'paid',
    'meta_data': [],
}


class MopeTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.mope = Mope()

    @mock.patch('requests.request')
    def test_call_api(self, mock_request):
        self.mope.call_api('POST', 'https://api.mope.sr/api', json={'amount': 1000})

        mock_request.assert_called_once_with(
            url='https://api.mope.sr/api',
            json={'amount': 1000},
            data=None,
            method='POST',
            params=None,
            headers={
                'User-Agent': 'Python Mope 0.0.3',
                'Content-Type': 'application/json',
                'Authorization': 'Bearer None'
            },
        )

    @mock.patch('requests.request')
    def test_shop_create_payment_request(self, mock_request):
        self.mope.shop.create_payment_request(
            amount=1000,
            description='test',
            order_id='test-1',
            currency='SRD',
            redirect_url='https://www.sup.com/products/1',
        )

        mock_request.assert_called_once_with(
            url='https://api.mope.sr/api/shop/payment_request',
            data=None,
            json={
                'amount': 1000,
                'order_id': 'test-1',
                'currency': 'SRD',
                'description': 'test',
                'redirect_url': 'https://www.sup.com/products/1'
            },
            method='POST',
            params=None,
            headers={
                'User-Agent': 'Python Mope 0.0.3',
                'Content-Type': 'application/json',
                'Authorization': 'Bearer None'
            },
        )

    @mock.patch('requests.request')
    def test_shop_get_payment_request(self, mock_request):
        mock_request.return_value = Mock(ok=True)
        mock_request.return_value.json.return_value = mock_payment_request

        mock_response = self.mope.shop.get_payment_request(payment_id='c43f24a3-df4f-43b7-9045-b454529369dc')

        self.assertTrue(isinstance(mock_response, PaymentRequest))
        self.assertTrue(isinstance(mock_response.currency, Currency))

        for key, value in mock_payment_request.items():
            if key == 'currency':
                for k, v in value.items():
                    self.assertTrue(getattr(mock_response.currency, k) == v)
            else:
                self.assertTrue(getattr(mock_response, key) == value)
