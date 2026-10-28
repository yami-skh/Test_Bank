from requests import Response
from src.main.api.requests.requester import Requester
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.create_user_response import CreateUserResponse
from http import HTTPStatus
import requests


class CreateUserRequester(Requester):
    def post(self, create_user_request: CreateUserRequest) -> CreateUserResponse | Response:
        url = self.base_url + "/admin/create"
        response = requests.post(
            url=url,
            headers=self.headers,
            json=create_user_request.model_dump()
        )
        self.response_spec(response)
        if response.status_code in (HTTPStatus.OK, HTTPStatus.CREATED):
            return CreateUserResponse(**response.json())
        return response



