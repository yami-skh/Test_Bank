from http import HTTPStatus

import requests
from requests import Response


from src.main.api.models.money_transfer_request import MoneyTransferRequest
from src.main.api.models.money_transfer_response import MoneyTransferResponse
from src.main.api.requests.requester import Requester


class MoneyTransferRequester(Requester):
    def post(self, money_transfer_request: MoneyTransferRequest) -> MoneyTransferResponse | Response:
        url = f"{self.base_url}/account/transfer"
        response = requests.post(
            url=url,
            json=money_transfer_request.model_dump(),
            headers=self.headers
        )
        self.response_spec(response)
        if response.status_code in (HTTPStatus.OK, HTTPStatus.CREATED):
            return MoneyTransferResponse(**response.json())
        return response