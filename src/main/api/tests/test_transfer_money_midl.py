import random

import pytest

from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.money_transfer_request import MoneyTransferRequest
from src.main.api.requests.account_deposit_requester import AccountDepositRequester
from src.main.api.requests.create_account_requester import CreateAccountRequester
from src.main.api.requests.create_user_requester import CreateUserRequester
from src.main.api.requests.money_transfer_requester import MoneyTransferRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


def generate_username():
    return "user" + str(random.randint(0, 999999))

@pytest.mark.api
class TestTransferMoneyMidl:
    def test_transfer_money_valid(self):
        username=generate_username()


        create_user_request = CreateUserRequest(username=username, password="Pas!w0rd", role="ROLE_USER")

        response = CreateUserRequester(
            request_spec=RequestSpecs.auth_headers(username="admin", password="123456"),
            response_spec=ResponseSpecs.request_ok()
        ).post(create_user_request)


        create_account_response_1 = CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password="Pas!w0rd"),
            response_spec=ResponseSpecs.request_create()
        ).post()


        create_account_response_2 = CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password="Pas!w0rd"),
            response_spec=ResponseSpecs.request_create()
        ).post()


        account_deposit_request = AccountDepositRequest(accountId=create_account_response_1.id, amount=8000)

        response = AccountDepositRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password="Pas!w0rd"),
            response_spec=ResponseSpecs.request_ok()
        ).post(account_deposit_request)


        money_transfer_request = MoneyTransferRequest(
            fromAccountId=create_account_response_1.id,
            toAccountId=create_account_response_2.id,
            amount=6000,
        )

        response = MoneyTransferRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password="Pas!w0rd"),
            response_spec=ResponseSpecs.request_ok()
        ).post(money_transfer_request)

        assert response.fromAccountIdBalance == account_deposit_request.amount - money_transfer_request.amount


    def test_transfer_money_invalid(self):
        username=generate_username()


        create_user_request = CreateUserRequest(username=username, password="Pas!w0rd", role="ROLE_USER")

        response = CreateUserRequester(
            request_spec=RequestSpecs.auth_headers(username="admin", password="123456"),
            response_spec=ResponseSpecs.request_ok()
        ).post(create_user_request)


        create_account_response_1 = CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password="Pas!w0rd"),
            response_spec=ResponseSpecs.request_create()
        ).post()


        create_account_response_2 = CreateAccountRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password="Pas!w0rd"),
            response_spec=ResponseSpecs.request_create()
        ).post()


        account_deposit_request = AccountDepositRequest(accountId=create_account_response_1.id, amount=8000)

        response = AccountDepositRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password="Pas!w0rd"),
            response_spec=ResponseSpecs.request_ok()
        ).post(account_deposit_request)


        money_transfer_request = MoneyTransferRequest(
            fromAccountId=create_account_response_1.id,
            toAccountId=create_account_response_2.id,
            amount=8001,
        )

        response = MoneyTransferRequester(
            request_spec=RequestSpecs.auth_headers(username=username, password="Pas!w0rd"),
            response_spec=ResponseSpecs.request_unprocessable()
        ).post(money_transfer_request)