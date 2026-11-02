import random
from http import HTTPStatus

from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.requests.account_deposit_requester import AccountDepositRequester
from src.main.api.requests.create_account_requester import CreateAccountRequester
from src.main.api.requests.create_user_requester import CreateUserRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


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

        # создаём б счёт со входом через пользователя, используя его токен
        create_account_response = CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password="Pas!w0rd"),
            response_spec=ResponseSpecs.request_create()

        ).post()

        # передаем в модель пополнения счёта id и сумму перевода
        account_deposit_request = AccountDepositRequest(accountId=create_account_response.id, amount=1000.0)
        # мы получаем результат после передачи данных пользователя и в конце делаем проверку, что баланс пополнен
        response = AccountDepositRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password="Pas!w0rd"),
            response_spec=ResponseSpecs.request_ok()
        ).post(account_deposit_request)

        assert response.balance == account_deposit_request.amount
        assert response.id == account_deposit_request.accountId




    def test_account_deposit_invalid(self):
        username = generate_username()
        create_user_request = CreateUserRequest(username=username, password="Pas!w0rd", role="ROLE_USER")

        response = CreateUserRequester(
            request_spec=RequestSpecs.auth_headers(username="admin", password="123456"),
            response_spec=ResponseSpecs.request_ok()
        ).post(create_user_request)

        assert create_user_request.username == response.username
        assert response.role == "ROLE_USER"

        create_account_response = CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password="Pas!w0rd"),
            response_spec=ResponseSpecs.request_create()
        ).post()


        account_deposit_request = AccountDepositRequest(accountId=create_account_response.id, amount=9001.0)

        response = AccountDepositRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password="Pas!w0rd"),
            response_spec=ResponseSpecs.request_bad()
        ).post(account_deposit_request)

        assert response.status_code == HTTPStatus.BAD_REQUEST







