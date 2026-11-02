import random

from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.user_credit_request import UserCreditRequest
from src.main.api.requests.create_account_requester import CreateAccountRequester

from src.main.api.requests.create_user_requester import CreateUserRequester
from src.main.api.requests.user_credit_requester import UserCreditRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


def generate_user():
    return "user" + str(random.randint(0, 999999))



class TestUserCreditMidl:
    def test_user_credit_valid(self):

        username = generate_user()

        create_user_request = CreateUserRequest(username=username, password="Pas!w0rd", role="ROLE_CREDIT_SECRET")

        response = CreateUserRequester(
            request_spec=RequestSpecs.auth_headers(username="admin", password="123456"),
            response_spec=ResponseSpecs.request_ok()
        ).post(create_user_request)


        create_account_response = CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password="Pas!w0rd"),
            response_spec=ResponseSpecs.request_create()
        ).post()

        # Ждём 201, ответ распаковывается в UserCreditResponse. В Swagger поле номера счёта
        # в ответе называется accountId, но API на самом деле возвращает id —
        # расхождение документации и реального ответа. Модель сделана по факту (поле id).
        user_credit_request = UserCreditRequest(accountId=create_account_response.id, amount=15000, termMonths=12)


        response = UserCreditRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password="Pas!w0rd"),
            response_spec=ResponseSpecs.request_create()
        ).post(user_credit_request)

        assert response.balance == create_account_response.balance + user_credit_request.amount



    def test_user_credit_invalid(self):

        username = generate_user()

        create_user_request = CreateUserRequest(username=username, password="Pas!w0rd", role="ROLE_CREDIT_SECRET")

        response = CreateUserRequester(
            request_spec=RequestSpecs.auth_headers(username="admin", password="123456"),
            response_spec=ResponseSpecs.request_ok()
        ).post(create_user_request)


        create_account_response = CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password="Pas!w0rd"),
            response_spec=ResponseSpecs.request_create()
        ).post()


        user_credit_request = UserCreditRequest(accountId=create_account_response.id, amount=15001, termMonths=12)

        # Ждём 400. В Swagger для превышения лимита указан 422 "Credit amount cannot exceed 15000",
        # но API на самом деле отвечает 400 "Amount must be between 5000 and 15000" —
        # расхождение документации и реального поведения. Тест написан по факту.
        response = UserCreditRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password="Pas!w0rd"),
            response_spec=ResponseSpecs.request_bad()
        ).post(user_credit_request)


        assert "Amount must be between 5000 and 15000" in response.text








