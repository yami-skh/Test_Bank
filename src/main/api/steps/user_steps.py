from src.main.api.foundation.endpoint import Endpoint
from src.main.api.foundation.requesters.crud_requester import CrudRequester
from src.main.api.foundation.requesters.validate_crud_requester import ValidateCrudRequester
from src.main.api.models.account_deposit_request import AccountDepositRequest

from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.steps.base_steps import BaseSteps


class UserSteps(BaseSteps):
    def create_account(self, create_user_request: CreateUserRequest):
        account_response = ValidateCrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.CREATE_USER_ACCOUNT,
            ResponseSpecs.request_create()
        ).post()

        return account_response

    def deposit(self, create_user_request: CreateUserRequest, account_deposit_request: AccountDepositRequest):
        deposit_response = ValidateCrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.ACCOUNT_DEPOSIT,
            ResponseSpecs.request_ok()
        ).post(account_deposit_request)

        return deposit_response

    def deposit_unauthorized(self, account_deposit_request: AccountDepositRequest):
        deposit_response = CrudRequester(
            RequestSpecs.unauth_headers(),
            Endpoint.ACCOUNT_DEPOSIT,
            ResponseSpecs.request_unauthorized()
        ).post(account_deposit_request)

        return deposit_response

    def deposit_invalid(self, create_user_request: CreateUserRequest, account_deposit_request: AccountDepositRequest):
        deposit_response = CrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.ACCOUNT_DEPOSIT,
            ResponseSpecs.request_bad()
        ).post(account_deposit_request)

        return deposit_response