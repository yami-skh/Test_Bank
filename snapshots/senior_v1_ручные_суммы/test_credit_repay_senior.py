import pytest

from src.main.api.models.credit_repay_request import CreditRepayRequest
from src.main.api.models.user_credit_request import UserCreditRequest


@pytest.mark.apis
class TestCreditRepay:
    def test_credit_repay_valid(self, api_manager, create_user_request):
        user = create_user_request(role="ROLE_CREDIT_SECRET")

        account = api_manager.user_steps.create_account(user)

        assert account.balance == 0

        credit_request = UserCreditRequest(accountId=account.id, amount=14000.0, termMonths=12)
        credit_response = api_manager.user_steps.user_credit(user, credit_request)

        assert credit_response.amount == 14000.0

        repay_request = CreditRepayRequest(creditId=credit_response.creditId, accountId=credit_response.id, amount=14000.0)
        repay_response = api_manager.user_steps.credit_repay(user, repay_request)

        assert repay_response.amountDeposited == 14000.0


    def test_credit_repay_invalid(self, api_manager, create_user_request):
        user = create_user_request(role="ROLE_CREDIT_SECRET")

        account = api_manager.user_steps.create_account(user)

        assert account.balance == 0

        credit_request = UserCreditRequest(accountId=account.id, amount=14000.0, termMonths=12)
        credit_response = api_manager.user_steps.user_credit(user, credit_request)

        assert credit_response.amount == 14000.0

        repay_request = CreditRepayRequest(creditId=credit_response.creditId, accountId=credit_response.id,
                                           amount=13999.0)
        repay_response = api_manager.user_steps.credit_repay_invalid(user, repay_request)

        assert "Credit balance" in repay_response.text









