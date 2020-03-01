from mope.models.payment import CreatePaymentResponse, PaymentRequest


class ShopResource:
    def __init__(self, client):
        self._client = client

    def create_payment_request(self, amount, description, order_id, currency, redirect_url):
        endpoint = '%s/shop/payment_request' % self._client.url_base
        response = self._client.call_api('POST', endpoint=endpoint, json={
            'amount': amount,
            'order_id': order_id,
            'currency': currency,
            'description': description,
            'redirect_url': redirect_url,
        })
        response.raise_for_status()
        return CreatePaymentResponse.from_json(response.json())

    def get_payment_request(self, payment_id):
        endpoint = '%s/shop/payment_request/%s' % (self._client.url_base, payment_id)
        response = self._client.call_api('GET', endpoint=endpoint)
        response.raise_for_status()
        return PaymentRequest.from_json(response.json())
