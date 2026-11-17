import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.user_credit_request import UserCreditRequest
from src.main.api.models.user_credit_response import UserCreditResponse
from src.main.db.crud.credit_crud import CreditCrudDb


@pytest.mark.api
class TestUserCredit:
    def test_user_credit(self, api_manager: ApiManager, credit_user: CreateUserRequest,
                         credit_account: CreateAccountResponse, db_session: Session) -> None:
        # --- Подготовка: запрос кредита на счёт кредитного пользователя ---
        credit_request = RandomModelGenerator.generate(UserCreditRequest)
        credit_request.accountId = credit_account.id

        expected_debt = -credit_request.amount

        # --- Действие: запрос кредита ---
        credit = api_manager.user_steps.user_credit(credit_user, credit_request)

        # --- Проверка: ответ API ---
        assert credit.amount == credit_request.amount, (
            f"Сумма кредита в ответе {credit.amount}, ожидали {credit_request.amount}"
        )
        assert credit.id == credit_account.id, (
            f"Кредит в ответе выдан на счёт {credit.id}, ожидали {credit_account.id}"
        )

        # --- Проверка: база данных ---
        credit_from_db = CreditCrudDb.get_credit_by_id(db_session, credit_id=credit.creditId)
        assert credit_from_db is not None, (
            f"Кредит {credit.creditId} не найден в БД"
        )
        assert credit_from_db.account_id == credit_account.id, (
            f"В БД кредит привязан к счёту {credit_from_db.account_id}, ожидали {credit_account.id}"
        )
        assert credit_from_db.balance == expected_debt, (
            f"В БД долг по кредиту {credit_from_db.balance}, ожидали {expected_debt}"
        )

    @pytest.mark.parametrize(
        "amount, termMonths",
        [
            (5000.0, 1),
            (7500.0, 30),
            (15000.0, 59),
            (13500.0, 60),
        ],
    )
    def test_user_credit_valid(self, api_manager: ApiManager, credit_user: CreateUserRequest,
                               credit_account: CreateAccountResponse, amount: float, termMonths: int) -> None:
        # --- Подготовка: запрос кредита с суммой и сроком на границах ---
        credit_request = UserCreditRequest(
            accountId=credit_account.id,
            amount=amount,
            termMonths=termMonths,
        )

        # --- Действие: запрос кредита ---
        credit = api_manager.user_steps.user_credit(credit_user, credit_request)

        # --- Проверка: ответ API ---
        assert credit.amount == credit_request.amount, (
            f"Сумма кредита в ответе {credit.amount}, ожидали {credit_request.amount}"
        )

    @pytest.mark.parametrize(
        "amount, termMonths, error_text",
        [
            (1.0, 12, "Amount must be between 5000 and 15000"),
            (4999.0, 15, "Amount must be between 5000 and 15000"),
            (15001.0, 19, "Amount must be between 5000 and 15000"),
            (130900.0, 37, "Amount must be between 5000 and 15000"),
            (-5000, 12, "Amount must be greater than 0"),
            (12000, 0, "Term months must be between 1 and 60"),
            (12000, 61, "Term months must be between 1 and 60"),
            (11000, -12, "Term months must be between 1 and 60"),
        ],
    )
    def test_user_credit_invalid(self, api_manager: ApiManager, credit_user: CreateUserRequest,
                                 credit_account: CreateAccountResponse, amount: float, termMonths: int,
                                 error_text: str) -> None:
        # --- Подготовка: запрос кредита с суммой или сроком вне лимита ---
        credit_request = UserCreditRequest(
            accountId=credit_account.id,
            amount=amount,
            termMonths=termMonths,
        )

        # --- Действие: запрос кредита вне лимита ---
        credit = api_manager.user_steps.user_credit_out_of_limit(credit_user, credit_request)

        # --- Проверка: ответ API ---
        assert error_text in credit.text, (
            f"В ответе нет ошибки «{error_text}»: {credit.text}"
        )

    def test_user_credit_second(self, api_manager: ApiManager, credit_user: CreateUserRequest,
                                credit_account: CreateAccountResponse, credit: UserCreditResponse) -> None:
        # --- Подготовка: запрос второго кредита, первый уже выдан ---
        second_credit_request = RandomModelGenerator.generate(UserCreditRequest)
        second_credit_request.accountId = credit_account.id

        # --- Действие: второй кредит ---
        # По Swagger здесь 403, по факту банк отдаёт 404 — шаг user_credit_invalid сделан по факту
        second_credit = api_manager.user_steps.user_credit_invalid(credit_user, second_credit_request)

        # --- Проверка: ответ API ---
        assert "Only one active credit allowed per user" in second_credit.text, (
            f"В ответе нет ошибки о втором кредите: {second_credit.text}"
        )

    def test_user_credit_forbidden(self, api_manager: ApiManager, user: CreateUserRequest,
                                   account: CreateAccountResponse, db_session: Session) -> None:
        # --- Подготовка: запрос кредита от обычного пользователя (ROLE_USER) ---
        credit_request = RandomModelGenerator.generate(UserCreditRequest)
        credit_request.accountId = account.id

        # --- Действие: запрос кредита без права ---
        response = api_manager.user_steps.user_credit_forbidden(user, credit_request)

        # --- Проверка: ответ API ---
        # тело ответа на 403 другое, чем у 404/422: не {"error": ...}, а {"title", "status", "detail", ...}
        assert "ROLE_CREDIT access required" in response.text, (
            f"В ответе нет ошибки о нехватке прав: {response.text}"
        )

        # --- Проверка: база данных ---
        assert CreditCrudDb.get_credits_by_account(db_session, account.id) == [], (
            f"У счёта {account.id} появился кредит в БД, хотя запрос отклонён (403)"
        )
