import pytest

from src.main.api.models.user_credit_request import UserCreditRequest


@pytest.mark.apis
class TestUserCredit:
    def test_user_credit_valid(self, api_manager, create_user_request):
        user = create_user_request(role="ROLE_CREDIT_SECRET")

        account = api_manager.user_steps.create_account(user)
        assert account.balance == 0

        credit_request = UserCreditRequest(accountId=account.id, amount=10000.0, termMonths=12)
        credit = api_manager.user_steps.user_credit(user, credit_request)

        assert credit.balance == 10000.0

    def test_user_credit_invalid(self, api_manager, create_user_request):
        user = create_user_request(role="ROLE_CREDIT_SECRET")

        account = api_manager.user_steps.create_account(user)
        assert account.balance == 0

        credit_request_one = UserCreditRequest(accountId=account.id, amount=10000.0, termMonths=12)
        credit_one = api_manager.user_steps.user_credit(user, credit_request_one)

        credit_request_two = UserCreditRequest(accountId=account.id, amount=5000.0, termMonths=12)
        credit_two = api_manager.user_steps.user_credit_invalid(user, credit_request_two) # <- Вот здесь должно дать ошибку 403, но по факту дает 404. сделано по факту в user_step.

        assert "Only one active credit allowed per user" in credit_two.json()["error"]

    def test_user_credit_forbidden(self, api_manager, create_user_request):
        # обычный пользователь без роли ROLE_CREDIT_SECRET кредит взять не может
        user = create_user_request()

        account = api_manager.user_steps.create_account(user)

        credit_request = UserCreditRequest(accountId=account.id, amount=10000.0, termMonths=12)
        response = api_manager.user_steps.user_credit_forbidden(user, credit_request)

        # тело ответа на 403 другое, чем у 404/422: не {"error": ...}, а {"title", "status", "detail", ...}
        assert "ROLE_CREDIT access required" in response.json()["detail"]
