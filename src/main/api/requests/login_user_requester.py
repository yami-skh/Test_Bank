import requests
from requests import Response

from src.main.api.models.login_user_request import LoginUserRequest
from src.main.api.requests.requester import Requester
from src.main.api.models.login_user_response import LoginUserResponse


class LoginUserRequester(Requester):
    def post(self, login_user_request: LoginUserRequest) -> LoginUserResponse | Response:
        url=f"{self.base_url}/auth/token/login"
        response = requests.post(
            url=url,
            json=login_user_request.model_dump(),
            headers=self.headers
        )
        self.response_spec(response)
        return LoginUserResponse(**response.json())
