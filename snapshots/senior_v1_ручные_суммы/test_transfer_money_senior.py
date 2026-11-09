import pytest

from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.money_transfer_request import MoneyTransferRequest


@pytest.mark.apis
class TestTransferMoney:
    def test_transfer_money_valid(self, api_manager, create_user_request):
        user = create_user_request()

        account_one = api_manager.user_steps.create_account(user)

        assert account_one.balance == 0

        account_two = api_manager.user_steps.create_account(user)

        assert account_two.balance == 0

        deposit_request = AccountDepositRequest(accountId=account_one.id, amount=5000.0)
        deposit = api_manager.user_steps.deposit(user, deposit_request)

        assert deposit.balance == 5000.0

        transfer_request = MoneyTransferRequest(fromAccountId=account_one.id, toAccountId=account_two.id, amount=2000.0)
        transfer = api_manager.user_steps.money_transfer(user, transfer_request)

        assert transfer.fromAccountIdBalance == deposit.balance - transfer_request.amount


    def test_transfer_money_invalid(self, api_manager, create_user_request):
        user = create_user_request()

        account_one = api_manager.user_steps.create_account(user)

        assert account_one.balance == 0

        account_two = api_manager.user_steps.create_account(user)

        assert account_two.balance == 0

        deposit_request = AccountDepositRequest(accountId=account_one.id, amount=5000.0)
        deposit = api_manager.user_steps.deposit(user, deposit_request)

        assert deposit.balance == 5000.0

        transfer_request = MoneyTransferRequest(fromAccountId=account_one.id, toAccountId=account_two.id, amount=5000.1)
        transfer = api_manager.user_steps.money_transfer_invalid(user, transfer_request)

        assert "Insufficient funds." in transfer.text



