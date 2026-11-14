from mope.models.payments import CreatePaymentResponse, CurrencyCode, PaymentRequest
from mope.transport import ApiTransport


class ShopResource:
    def __init__(self, client: ApiTransport) -> None:
        self._client = client

    def create_payment_request(
        self,
        amount: int,
        description: str,
        order_id: str,
        currency: CurrencyCode,
        redirect_url: str,
    ) -> CreatePaymentResponse:
        """
        makes a payment request
        """

        endpoint = "shop/payment_request"
        response = self._client.call_api(
            "POST",
            endpoint=endpoint,
            json={
                "amount": amount,
                "order_id": order_id,
                "currency": currency,
                "description": description,
                "redirect_url": redirect_url,
            },
        )
        response.raise_for_status()
        return CreatePaymentResponse.from_json(response.json())

    def get_payment_request(self, payment_id: str) -> PaymentRequest:
        """
        fetches a payment request given a payment ID
        """

        endpoint = f"shop/payment_request/{payment_id}"
        response = self._client.call_api("GET", endpoint=endpoint)
        response.raise_for_status()
        return PaymentRequest.from_json(response.json())
