import pytest

from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.money_transfer_request import MoneyTransferRequest

MAX_DEPOSIT = 9000.0 # Максимальная сумма пополнения по требованиям проекта

@pytest.mark.apis
class TestTransferMoney:
    def test_transfer_money(self, api_manager, create_user_request):
        user = create_user_request()

        account_one = api_manager.user_steps.create_account(user)
        assert account_one.balance == 0

        account_two = api_manager.user_steps.create_account(user)
        assert account_two.balance == 0

        deposit_request = RandomModelGenerator.generate(AccountDepositRequest)
        deposit_request.accountId = account_one.id
        deposit = api_manager.user_steps.deposit(user, deposit_request)
        assert deposit.balance == account_one.balance + deposit_request.amount

        transfer_request = MoneyTransferRequest(fromAccountId=account_one.id, toAccountId=account_two.id, amount=deposit.balance / 2)
        transfer = api_manager.user_steps.money_transfer(user, transfer_request)
        assert transfer.fromAccountIdBalance == deposit.balance - transfer_request.amount


    @pytest.mark.parametrize("amount", [500.0, 501.0, 5000.0, 9999.0, 10000.0])
    def test_transfer_money_valid(self, api_manager, create_user_request, amount):
        user = create_user_request()

        account_one = api_manager.user_steps.create_account(user)
        assert account_one.balance == 0

        account_two = api_manager.user_steps.create_account(user)
        assert account_two.balance == 0

        first_deposit_request = AccountDepositRequest(accountId=account_one.id, amount=MAX_DEPOSIT)
        deposit = api_manager.user_steps.deposit(user, first_deposit_request)

        second_deposit_request = AccountDepositRequest(accountId=account_one.id, amount=MAX_DEPOSIT)
        deposit = api_manager.user_steps.deposit(user, second_deposit_request)


        transfer_request = MoneyTransferRequest(fromAccountId=account_one.id, toAccountId=account_two.id, amount=amount)
        transfer = api_manager.user_steps.money_transfer(user, transfer_request)

        assert transfer.fromAccountIdBalance == deposit.balance - transfer_request.amount


    @pytest.mark.parametrize("amount", [250.0, 499.0, 10001.0, 15000.0])
    def test_transfer_money_invalid(self, api_manager, create_user_request, amount):
        user = create_user_request()

        account_one = api_manager.user_steps.create_account(user)
        assert account_one.balance == 0

        account_two = api_manager.user_steps.create_account(user)
        assert account_two.balance == 0

        first_deposit_request = AccountDepositRequest(accountId=account_one.id, amount=MAX_DEPOSIT)
        api_manager.user_steps.deposit(user, first_deposit_request)

        second_deposit_request = AccountDepositRequest(accountId=account_one.id, amount=MAX_DEPOSIT)
        api_manager.user_steps.deposit(user, second_deposit_request)

        transfer_request = MoneyTransferRequest(fromAccountId=account_one.id, toAccountId=account_two.id, amount=amount)
        transfer = api_manager.user_steps.money_transfer_out_of_limit(user, transfer_request)
        assert "Amount must be between 500 and 10000" in transfer.text # текст ответа малость отличается от текста в свагере


    def test_transfer_money_insufficient_funds(self, api_manager, create_user_request):
        user = create_user_request()

        account_one = api_manager.user_steps.create_account(user)
        assert account_one.balance == 0

        account_two = api_manager.user_steps.create_account(user)
        assert account_two.balance == 0

        deposit_request = RandomModelGenerator.generate(AccountDepositRequest)
        deposit_request.accountId = account_one.id
        deposit = api_manager.user_steps.deposit(user, deposit_request)

        transfer_request = MoneyTransferRequest(fromAccountId=account_one.id, toAccountId=account_two.id, amount=deposit.balance + 0.1)
        transfer = api_manager.user_steps.money_transfer_invalid(user, transfer_request)
        assert "Insufficient funds" in transfer.text






