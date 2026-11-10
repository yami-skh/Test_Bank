import pytest

from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.models.account_deposit_request import AccountDepositRequest



@pytest.mark.api
class TestAccountDepositSenior:
    def test_account_deposit(self, api_manager, create_user_request):
        user = create_user_request()

        account = api_manager.user_steps.create_account(user)
        assert account.balance == 0

        deposit_request = RandomModelGenerator.generate(AccountDepositRequest)
        deposit_request.accountId = account.id
        deposit = api_manager.user_steps.deposit(user, deposit_request)
        assert deposit.balance == account.balance + deposit_request.amount

        account_after = api_manager.user_steps.get_account(user, account.id)
        assert account_after.balance == account.balance + deposit_request.amount


    @pytest.mark.parametrize("amount", [1000.0, 4500, 9000.0])
    def test_account_deposit_valid(self, api_manager, create_user_request, amount):
        user = create_user_request()
        account = api_manager.user_steps.create_account(user)
        assert account.balance == 0

        deposit_request = AccountDepositRequest(accountId=account.id, amount=amount)
        deposit = api_manager.user_steps.deposit(user, deposit_request)
        assert deposit.balance == account.balance + deposit_request.amount

        account_after = api_manager.user_steps.get_account(user, account.id)
        assert account_after.balance == account.balance + deposit_request.amount

    @pytest.mark.parametrize("amount", [450.0, 999.0, 9001.0, 15000.0])
    def test_account_deposit_invalid(self, api_manager, create_user_request, amount):
        user = create_user_request()
        account = api_manager.user_steps.create_account(user)
        assert account.balance == 0

        deposit_request = AccountDepositRequest(accountId=account.id, amount=amount)
        deposit = api_manager.user_steps.deposit_invalid(user, deposit_request)
        assert "Amount must be between 1000 and 9000" in deposit.text

        account_after = api_manager.user_steps.get_account(user, account.id)
        assert account_after.balance == account.balance

    def test_account_deposit_unauthorized(self, api_manager):
        deposit_request = RandomModelGenerator.generate(AccountDepositRequest)
        deposit_response = api_manager.user_steps.deposit_unauthorized(deposit_request)
        assert "JWT Token not found" in deposit_response.text




