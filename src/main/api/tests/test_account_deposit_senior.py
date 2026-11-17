import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.db.crud.account_crud import AccountCrudDb
from src.main.db.crud.transaction_crud import TransactionCrudDb


@pytest.mark.api
class TestAccountDeposit:
    def test_account_deposit(self, api_manager: ApiManager, user: CreateUserRequest,
                             account: CreateAccountResponse, db_session: Session) -> None:
        # --- Подготовка: пополнение случайной суммой ---
        deposit_request = RandomModelGenerator.generate(AccountDepositRequest)
        deposit_request.accountId = account.id
        expected_balance = account.balance + deposit_request.amount

        # --- Действие: пополнение ---
        deposit = api_manager.user_steps.deposit(user, deposit_request)

        # --- Проверка: ответ API ---
        assert deposit.balance == expected_balance, (
            f"Баланс в ответе на пополнение {deposit.balance}, ожидали {expected_balance}"
        )

        # --- Проверка: база данных ---
        account_from_db = AccountCrudDb.get_account_by_id(db_session, account_id=account.id)
        assert account_from_db is not None, f"Счёт {account.id} не найден в БД"
        assert account_from_db.balance == expected_balance, (
            f"Баланс в БД {account_from_db.balance}, ожидали {expected_balance}"
        )

        deposits_from_db = TransactionCrudDb.get_deposits(db_session, account_id=account.id)
        assert len(deposits_from_db) == 1, (
            f"Пополнений счёта {account.id} в БД {len(deposits_from_db)}, "
            f"ожидали 1: {deposits_from_db}"
        )

    @pytest.mark.parametrize("amount", [1000.0, 4500.0, 9000.0])
    def test_account_deposit_valid(self, api_manager: ApiManager, user: CreateUserRequest,
                                   account: CreateAccountResponse, amount: float, db_session: Session) -> None:
        # --- Подготовка: пополнение суммой на границе лимита ---
        deposit_request = AccountDepositRequest(accountId=account.id, amount=amount)
        expected_balance = account.balance + deposit_request.amount

        # --- Действие: пополнение ---
        deposit = api_manager.user_steps.deposit(user, deposit_request)

        # --- Проверка: ответ API ---
        assert deposit.balance == expected_balance, (
            f"Баланс в ответе на пополнение {deposit.balance}, ожидали {expected_balance}"
        )

        # --- Проверка: база данных ---
        account_from_db = AccountCrudDb.get_account_by_id(db_session, account_id=account.id)
        assert account_from_db is not None, f"Счёт {account.id} не найден в БД"
        assert account_from_db.balance == expected_balance, (
            f"Баланс в БД {account_from_db.balance}, ожидали {expected_balance}"
        )

    @pytest.mark.parametrize("amount", [450.0, 999.0, 9001.0, 15000.0])
    def test_account_deposit_invalid(self, api_manager: ApiManager, user: CreateUserRequest,
                                     account: CreateAccountResponse, amount: float, db_session: Session) -> None:
        # --- Подготовка: пополнение суммой вне лимита ---
        deposit_request = AccountDepositRequest(accountId=account.id, amount=amount)
        expected_balance = account.balance  # пополнение отклонено — баланс не меняется

        # --- Действие: пополнение вне лимита ---
        deposit = api_manager.user_steps.deposit_invalid(user, deposit_request)

        # --- Проверка: ответ API ---
        assert "Amount must be between 1000 and 9000" in deposit.text, (
            f"В ответе нет ошибки о лимите пополнения: {deposit.text}"
        )

        # --- Проверка: база данных ---
        account_from_db = AccountCrudDb.get_account_by_id(db_session, account_id=account.id)
        assert account_from_db is not None, f"Счёт {account.id} не найден в БД"
        assert account_from_db.balance == expected_balance, (
            f"Баланс в БД {account_from_db.balance}, ожидали {expected_balance} — "
            f"пополнение отклонено, баланс не должен был измениться"
        )

    def test_account_deposit_unauthorized(self, api_manager: ApiManager) -> None:
        # --- Подготовка: запрос без авторизации ---
        deposit_request = RandomModelGenerator.generate(AccountDepositRequest)

        # --- Действие: пополнение без токена ---
        deposit_response = api_manager.user_steps.deposit_unauthorized(deposit_request)

        # --- Проверка: ответ API ---
        assert "JWT Token not found" in deposit_response.text, (
            f"В ответе нет ошибки об отсутствии токена: {deposit_response.text}"
        )
