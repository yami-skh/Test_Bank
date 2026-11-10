import pytest

from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.credit_repay_request import CreditRepayRequest
from src.main.api.models.money_transfer_request import MoneyTransferRequest
from src.main.api.models.user_credit_request import UserCreditRequest


MAX_DEPOSIT = 9000.0

@pytest.mark.api
class TestCreditRepay:
    def test_credit_repay_valid(self, api_manager, create_user_request):
        user = create_user_request(role="ROLE_CREDIT_SECRET")

        account = api_manager.user_steps.create_account(user)
        assert account.balance == 0

        credit_request = RandomModelGenerator.generate(UserCreditRequest)
        credit_request.accountId = account.id
        credit = api_manager.user_steps.user_credit(user, credit_request)

        repay_request = CreditRepayRequest(
            creditId=credit.creditId,
            accountId=account.id,
            amount=credit.amount,
        )
        repay_response = api_manager.user_steps.credit_repay(user, repay_request)
        assert repay_response.amountDeposited == repay_request.amount
        assert repay_response.creditId == credit.creditId

        account_after = api_manager.user_steps.get_account(user, account.id)
        assert account_after.balance == credit.balance - repay_request.amount

        credit_history = api_manager.user_steps.get_credit_history(user)
        credits = [c for c in credit_history.credits if c.creditId == credit.creditId]
        assert len(credits) == 1
        assert credits[0].balance == -credit.amount + repay_request.amount

    @pytest.mark.parametrize("offset, error_text", [
        (-1.0, "The amount is not enough"),
        (-3000, "The amount is not enough"),
        (1.0, "Repayment amount exceeds remaining debt"),
        (500.0, "Repayment amount exceeds remaining debt"),
    ],
                             )
    def test_credit_repay_invalid(self, api_manager, create_user_request, offset, error_text):
        user = create_user_request(role="ROLE_CREDIT_SECRET")

        account = api_manager.user_steps.create_account(user)
        assert account.balance == 0

        deposit_request = RandomModelGenerator.generate(AccountDepositRequest)
        deposit_request.accountId = account.id
        deposit = api_manager.user_steps.deposit(user, deposit_request)

        credit_request = RandomModelGenerator.generate(UserCreditRequest)
        credit_request.accountId = account.id
        credit = api_manager.user_steps.user_credit(user, credit_request)

        repay_request = CreditRepayRequest(
            creditId=credit.creditId,
            accountId=account.id,
            amount=credit.amount + offset
        )
        repay_response = api_manager.user_steps.credit_repay_invalid(user, repay_request)
        assert error_text in repay_response.text

        account_after = api_manager.user_steps.get_account(user, account.id)
        assert account_after.balance == credit.balance

        credit_history = api_manager.user_steps.get_credit_history(user)
        credits = [c for c in credit_history.credits if c.creditId == credit.creditId]
        assert len(credits) == 1
        assert credits[0].balance == -credit.amount

    def test_credit_repay_insufficient_funds(self, api_manager, create_user_request):
        user = create_user_request(role="ROLE_CREDIT_SECRET")

        account_one = api_manager.user_steps.create_account(user)
        account_two = api_manager.user_steps.create_account(user)

        credit_request = RandomModelGenerator.generate(UserCreditRequest)
        credit_request.accountId = account_one.id
        credit = api_manager.user_steps.user_credit(user, credit_request)

        transfer_request = MoneyTransferRequest(
            fromAccountId=account_one.id,
            toAccountId=account_two.id,
            amount=credit.amount / 2)
        transfer = api_manager.user_steps.money_transfer(user, transfer_request)

        repay_request = CreditRepayRequest(
            creditId=credit.creditId,
            accountId=account_one.id,
            amount=credit.amount,
        )
        repay_response = api_manager.user_steps.credit_repay_invalid(user, repay_request)
        assert "Insufficient funds" in repay_response.text

        account_after = api_manager.user_steps.get_account(user, account_one.id)
        assert account_after.balance == transfer.fromAccountIdBalance

        credit_history = api_manager.user_steps.get_credit_history(user)
        credits = [c for c in credit_history.credits if c.creditId == credit.creditId]
        assert len(credits) == 1
        assert credits[0].balance == -credit.amount

    def test_credit_repay_twice(self, api_manager, create_user_request):
        user = create_user_request(role="ROLE_CREDIT_SECRET")

        account = api_manager.user_steps.create_account(user)

        deposit_request = AccountDepositRequest(
            accountId=account.id,
            amount=MAX_DEPOSIT
        )
        api_manager.user_steps.deposit(user, deposit_request)
        api_manager.user_steps.deposit(user, deposit_request)

        credit_request = RandomModelGenerator.generate(UserCreditRequest)
        credit_request.accountId = account.id
        credit = api_manager.user_steps.user_credit(user, credit_request)

        repay_request = CreditRepayRequest(
            creditId=credit.creditId,
            accountId=account.id,
            amount=credit.amount,
        )
        api_manager.user_steps.credit_repay(user, repay_request)
        account_after_first = api_manager.user_steps.get_account(user, account.id)

        repay_response_second = api_manager.user_steps.credit_repay_already_repaid(user, repay_request)
        assert "already been repaid" in repay_response_second.text

        account_after_second = api_manager.user_steps.get_account(user, account.id)
        assert account_after_second.balance == account_after_first.balance

        credit_history = api_manager.user_steps.get_credit_history(user)
        credits = [c for c in credit_history.credits if c.creditId == credit.creditId]
        assert len(credits) == 1
        assert credits[0].balance == -credit.amount + repay_request.amount

