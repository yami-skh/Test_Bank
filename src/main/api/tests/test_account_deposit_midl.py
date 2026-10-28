import pytest
import requests
import random

from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.login_user_request import LoginUserRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.models.login_user_response import LoginUserResponse
from src.main.api.requests.creat_account_requster import CreateAccountRequester
from src.main.api.requests.login_user_requester import LoginUserRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.requests.requester import Requester
from src.main.api.requests.create_user_requester import CreateUserRequester

# генерируем рандом логин по вызову функции в методе
def generate_username():
    return "user" + str(random.randint(0, 999999))

class TestAccountDepositMidl:
    def test_account_deposit_valid(self):
        # присвоили сгенерированное имя переменной один раз при старте метода
        username = generate_username()

        # логинимся за админа в респонс, берём его токен и создаём пользователя, всё делается
        #за кулисами через реквесторы, спексы и модели
        create_user_request = CreateUserRequest(username=username, password="Pas!w0rd", role="ROLE_USER" )

        response = CreateUserRequester(
            request_spec=RequestSpecs.auth_headers(username="admin", password="123456"),
            response_spec=ResponseSpecs.request_ok()
        ).post(create_user_request)

        assert create_user_request.username == response.username
        assert response.role == "ROLE_USER"

        # создаём б счёт входя через пользователя, используя его токен
        create_account_response = CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password="Pas!w0rd"),
            response_spec=ResponseSpecs.request_create()

        ).post()


