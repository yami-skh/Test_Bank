import pytest

from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.create_user_request import CreateUserRequest



@pytest.mark.apis
class TestAccountDepositSenior:
    def test_account_deposit_valid(self, api_manager):
        user = CreateUserRequest(username="Yami3", password="Pas!w0rd", role="ROLE_USER")
        api_manager.admin_steps.create_user(user)

        account = api_manager.user_steps.create_account(user)
        assert account.balance == 0

        deposit_request = AccountDepositRequest(accountId=account.id, amount=5000)
        deposit = api_manager.user_steps.deposit(user, deposit_request)
        assert deposit.balance == 5000


    def test_account_deposit_invalid(self, api_manager):
        user = CreateUserRequest(username="Yami4", password="Pas!w0rd", role="ROLE_USER")
        api_manager.admin_steps.create_user(user)

        account = api_manager.user_steps.create_account(user)
        assert account.balance == 0

        deposit_request = AccountDepositRequest(accountId=account.id, amount=9001)
        deposit = api_manager.user_steps.deposit_invalid(user, deposit_request)

        assert deposit.status_code == 400
        assert "Amount must be between 1000 and 9000" in deposit.text

    def test_account_deposit_unauthorized(self, api_manager):
        deposit_request = AccountDepositRequest(accountId=1, amount=9000)
        deposit_response = api_manager.user_steps.deposit_unauthorized(deposit_request)

        assert "JWT Token not found" in deposit_response.text




