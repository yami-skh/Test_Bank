import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.configs.constants import MAX_DEPOSIT
from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.credit_repay_request import CreditRepayRequest
from src.main.api.models.credit_repay_response import CreditRepayResponse
from src.main.api.models.money_transfer_request import MoneyTransferRequest
from src.main.api.models.money_transfer_response import MoneyTransferResponse
from src.main.api.models.user_credit_request import UserCreditRequest
from src.main.api.models.user_credit_response import UserCreditResponse


# Кредит на пустой счёт
@pytest.fixture
def credit(api_manager: ApiManager, credit_user: CreateUserRequest,
           credit_account: CreateAccountResponse) -> UserCreditResponse:
    credit_request = RandomModelGenerator.generate(UserCreditRequest)
    credit_request.accountId = credit_account.id
    credit_response = api_manager.user_steps.user_credit(credit_user, credit_request)
    return credit_response


# 18000 на счёт, потом кредит
@pytest.fixture
def funded_credit(api_manager: ApiManager, credit_user: CreateUserRequest,
                  credit_account: CreateAccountResponse) -> UserCreditResponse:
    deposit_request = AccountDepositRequest(accountId=credit_account.id, amount=MAX_DEPOSIT)
    api_manager.user_steps.deposit(credit_user, deposit_request)
    api_manager.user_steps.deposit(credit_user, deposit_request)
    credit_request = RandomModelGenerator.generate(UserCreditRequest)
    credit_request.accountId = credit_account.id
    credit_response = api_manager.user_steps.user_credit(credit_user, credit_request)
    return credit_response


# Кредит, половина ушла на второй счёт — на погашение не хватает
@pytest.fixture
def spent_credit(api_manager: ApiManager, credit_user: CreateUserRequest,
                 credit: UserCreditResponse, credit_account: CreateAccountResponse,
                 second_credit_account: CreateAccountResponse) -> MoneyTransferResponse:
    transfer_request = MoneyTransferRequest(
        fromAccountId=credit_account.id,
        toAccountId=second_credit_account.id,
        amount=credit.amount / 2)
    transfer_response = api_manager.user_steps.money_transfer(credit_user, transfer_request)
    return transfer_response


# Кредит из funded_credit уже погашен один раз
@pytest.fixture
def repaid_credit(api_manager: ApiManager, credit_user: CreateUserRequest,
                  credit_account: CreateAccountResponse,
                  funded_credit: UserCreditResponse) -> CreditRepayResponse:
    repay_request = CreditRepayRequest(
        creditId=funded_credit.creditId,
        accountId=credit_account.id,
        amount=funded_credit.amount,
    )
    repay_response = api_manager.user_steps.credit_repay(credit_user, repay_request)
    return repay_response
