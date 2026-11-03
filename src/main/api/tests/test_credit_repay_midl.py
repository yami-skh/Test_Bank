import pytest
import random

from src.main.api.models import user_credit_response
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.credit_repay_request import CreditRepayRequest
from src.main.api.models.user_credit_request import UserCreditRequest
from src.main.api.requests.create_account_requester import CreateAccountRequester
from src.main.api.requests.create_user_requester import CreateUserRequester
from src.main.api.requests.credit_repay_requester import CreditRepayRequester
from src.main.api.requests.user_credit_requester import UserCreditRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


def generate_username():
    return "user"+str(random.randint(1, 99999999))

@pytest.mark.api
class TestCreditRepayMidl:
    def test_credit_repay_valid(self):
        username = generate_username()

        create_user_request = CreateUserRequest(username=username, password="Pas!w0rd", role="ROLE_CREDIT_SECRET")

        response = CreateUserRequester(
            request_spec=RequestSpecs.auth_headers(username="admin", password="123456"),
            response_spec=ResponseSpecs.request_ok()
        ).post(create_user_request)


        create_account_response = CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password="Pas!w0rd"),
            response_spec=ResponseSpecs.request_create()
        ).post()

        user_credit_request = UserCreditRequest(accountId=create_account_response.id, amount=14999.0, termMonths=12)

        response = UserCreditRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password="Pas!w0rd"),
            response_spec=ResponseSpecs.request_create()
        ).post(user_credit_request)

        assert response.balance == create_account_response.balance + user_credit_request.amount


        credit_repay_request = CreditRepayRequest(creditId=response.creditId, accountId=response.id, amount=14999.0)

        response = CreditRepayRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password="Pas!w0rd"),
            response_spec=ResponseSpecs.request_ok()
        ).post(credit_repay_request)

        assert response.amountDeposited == credit_repay_request.amount
        assert response.creditId == credit_repay_request.creditId



    def test_credit_repay_invalid(self):
        username = generate_username()

        create_user_request = CreateUserRequest(username=username, password="Pas!w0rd", role="ROLE_CREDIT_SECRET")

        response = CreateUserRequester(
            request_spec=RequestSpecs.auth_headers(username="admin", password="123456"),
            response_spec=ResponseSpecs.request_ok()
        ).post(create_user_request)

        create_account_response = CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password="Pas!w0rd"),
            response_spec=ResponseSpecs.request_create()
        ).post()

        user_credit_request = UserCreditRequest(accountId=create_account_response.id, amount=14999.0, termMonths=12)

        response = UserCreditRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password="Pas!w0rd"),
            response_spec=ResponseSpecs.request_create()
        ).post(user_credit_request)

        assert response.balance == create_account_response.balance + user_credit_request.amount

        credit_repay_request = CreditRepayRequest(creditId=response.creditId, accountId=response.id, amount=14998.0)

        response = CreditRepayRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password="Pas!w0rd"),
            response_spec=ResponseSpecs.request_unprocessable()
        ).post(credit_repay_request)
