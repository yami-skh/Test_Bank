import pytest

from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.models.user_credit_request import UserCreditRequest


@pytest.mark.api
class TestUserCredit:
    def test_user_credit(self, api_manager, create_user_request):
        user = create_user_request(role="ROLE_CREDIT_SECRET")

        account = api_manager.user_steps.create_account(user)
        assert account.balance == 0

        credit_request = RandomModelGenerator.generate(UserCreditRequest)
        credit_request.accountId = account.id
        credit = api_manager.user_steps.user_credit(user, credit_request)
        assert credit.balance == credit_request.amount
        assert credit.id == account.id

        credit_history = api_manager.user_steps.get_credit_history(user)
        credits = [c for c in credit_history.credits if c.creditId == credit.creditId]
        assert len(credits) == 1
        assert credits[0].accountId == account.id
        assert credits[0].balance == -credit_request.amount

    @pytest.mark.parametrize(
        "amount, termMonths", [
            (5000.0, 1),
            (7500.0, 30),
            (15000.0, 59),
            (13500.0, 60),
        ],
    )
    def test_user_credit_valid(self, api_manager, create_user_request, amount, termMonths):
        user = create_user_request(role="ROLE_CREDIT_SECRET")

        account = api_manager.user_steps.create_account(user)
        assert account.balance == 0

        credit_request = UserCreditRequest(
            accountId=account.id,
            amount=amount,
            termMonths=termMonths
        )
        credit = api_manager.user_steps.user_credit(user, credit_request)
        assert credit.balance == credit_request.amount
        assert credit.id == account.id

    @pytest.mark.parametrize(
        "amount, termMonths, error_text", [
            (1.0, 12, "Amount must be between 5000 and 15000"),
            (4999.0, 15, "Amount must be between 5000 and 15000"),
            (15001.0, 19, "Amount must be between 5000 and 15000"),
            (130900.0, 37, "Amount must be between 5000 and 15000"),
            (-5000, 12, "Amount must be greater than 0"),
            (12000, 0, "Term months must be between 1 and 60"),
            (12000, 61, "Term months must be between 1 and 60"),
            (11000, -12, "Term months must be between 1 and 60"),
        ]
    )
    def test_user_credit_invalid(self, api_manager, create_user_request, amount, termMonths, error_text):
        user = create_user_request(role="ROLE_CREDIT_SECRET")

        account = api_manager.user_steps.create_account(user)
        assert account.balance == 0

        credit_request = UserCreditRequest(
            accountId=account.id,
            amount=amount,
            termMonths=termMonths
        )
        credit = api_manager.user_steps.user_credit_out_of_limit(user, credit_request)

        account_after = api_manager.user_steps.get_account(user, account.id)
        assert account_after.balance == account.balance
        assert error_text in credit.text

    def test_user_credit_second(self, api_manager, create_user_request):
        user = create_user_request(role="ROLE_CREDIT_SECRET")

        account = api_manager.user_steps.create_account(user)
        assert account.balance == 0

        credit_request_one = RandomModelGenerator.generate(UserCreditRequest)
        credit_request_one.accountId = account.id
        api_manager.user_steps.user_credit(user, credit_request_one)

        credit_request_two = RandomModelGenerator.generate(UserCreditRequest)
        credit_request_two.accountId = account.id
        # Вот здесь должно дать ошибку 403, но по факту дает 404. сделано по факту в user_step.
        credit_two = api_manager.user_steps.user_credit_invalid(user, credit_request_two)

        assert "Only one active credit allowed per user" in credit_two.text

    def test_user_credit_forbidden(self, api_manager, create_user_request):
        user = create_user_request()

        account = api_manager.user_steps.create_account(user)

        credit_request = RandomModelGenerator.generate(UserCreditRequest)
        credit_request.accountId = account.id
        response = api_manager.user_steps.user_credit_forbidden(user, credit_request)

        account_after = api_manager.user_steps.get_account(user, account.id)
        assert account_after.balance == account.balance
        assert account_after.transactions == []

        # тело ответа на 403 другое, чем у 404/422: не {"error": ...}, а {"title", "status", "detail", ...}
        assert "ROLE_CREDIT access required" in response.text
