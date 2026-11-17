import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.configs.constants import MAX_DEPOSIT
from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.account_deposit_response import AccountDepositResponse
from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.create_user_request import CreateUserRequest


# Счёт обычного пользователя
@pytest.fixture
def account(api_manager: ApiManager, user: CreateUserRequest) -> CreateAccountResponse:
    return api_manager.user_steps.create_account(user)


# Второй счёт того же пользователя
@pytest.fixture
def second_account(api_manager: ApiManager, user: CreateUserRequest) -> CreateAccountResponse:
    return api_manager.user_steps.create_account(user)


# Счёт кредитного пользователя
@pytest.fixture
def credit_account(api_manager: ApiManager, credit_user: CreateUserRequest) -> CreateAccountResponse:
    return api_manager.user_steps.create_account(credit_user)


# Второй счёт кредитного пользователя
@pytest.fixture
def second_credit_account(api_manager: ApiManager, credit_user: CreateUserRequest) -> CreateAccountResponse:
    return api_manager.user_steps.create_account(credit_user)


# Счёт с одним случайным пополнением
@pytest.fixture
def funded_account(api_manager: ApiManager, user: CreateUserRequest,
                   account: CreateAccountResponse) -> AccountDepositResponse:
    deposit_request = RandomModelGenerator.generate(AccountDepositRequest)
    deposit_request.accountId = account.id
    deposit = api_manager.user_steps.deposit(user, deposit_request)
    return deposit


# Счёт с 18000 (два пополнения по 9000)
@pytest.fixture
def max_funded_account(api_manager: ApiManager, user: CreateUserRequest,
                       account: CreateAccountResponse) -> AccountDepositResponse:
    deposit_request = AccountDepositRequest(
        accountId=account.id,
        amount=MAX_DEPOSIT,
    )
    api_manager.user_steps.deposit(user, deposit_request)
    deposit = api_manager.user_steps.deposit(user, deposit_request)
    return deposit

