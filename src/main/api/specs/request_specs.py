import requests

from src.main.api.models.login_user_request import LoginUserRequest
from src.main.api.models.login_user_response import LoginUserResponse


class RequestSpecs:
    BASE_URL = "http://localhost:4111/api"
    @staticmethod
    def base_headers():
        return {
            "Content-Type": "application/json",
            "accept": "application/json"
        }

    @staticmethod
    def auth_headers(username: str, password: str):
        login_user_request = LoginUserRequest(username=username, password=password)
        response = requests.post(
            url="http://localhost:4111/api/auth/token/login",
            json=login_user_request.model_dump(),
            headers=RequestSpecs.base_headers()
        )
        if response.status_code == 200:
            login_user_response = LoginUserResponse(**response.json())
            token = login_user_response.token

            headers = RequestSpecs.base_headers()
            headers["Authorization"] = f"Bearer {token}"
            return {"headers": headers, "base_url": RequestSpecs.BASE_URL}
        raise Exception(f"Ошибка авторизации {response.status_code} {response.text}")

    @staticmethod
    def unauth_headers():
        return {
            "headers": RequestSpecs.base_headers(),
            "base_url": RequestSpecs.BASE_URL
        }