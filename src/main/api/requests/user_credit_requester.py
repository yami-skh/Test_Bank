from http import HTTPStatus

import requests
from requests import Response

from src.main.api.models.user_credit_request import UserCreditRequest
from src.main.api.models.user_credit_response import UserCreditResponse
from src.main.api.requests.requester import Requester


class UserCreditRequester(Requester):
    def post(self, user_credit_request: UserCreditRequest) -> UserCreditResponse | Response:
        url = f"{self.base_url}/credit/request"
        response = requests.post(
            url=url,
            json=user_credit_request.model_dump(),
            headers=self.headers
        )

        self.response_spec(response)
        if response.status_code in (HTTPStatus.OK, HTTPStatus.CREATED):
            return UserCreditResponse(**response.json())
        return response