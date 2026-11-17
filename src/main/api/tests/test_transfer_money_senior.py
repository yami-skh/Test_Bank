import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.account_deposit_response import AccountDepositResponse
from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.money_transfer_request import MoneyTransferRequest
from src.main.api.utils import find_transactions_by_type
from src.main.db.crud.account_crud import AccountCrudDb


@pytest.mark.api
class TestTransferMoney:
    def test_transfer_money(self, api_manager: ApiManager, user: CreateUserRequest,
                            funded_account: AccountDepositResponse, second_account: CreateAccountResponse,
                            db_session: Session) -> None:
        # --- Подготовка: перевод половины денег на второй счёт ---
        transfer_request = MoneyTransferRequest(
            fromAccountId=funded_account.id,
            toAccountId=second_account.id,
            amount=funded_account.balance / 2,
        )
        expected_sender_balance = funded_account.balance - transfer_request.amount
        expected_receiver_balance = second_account.balance + transfer_request.amount

        # --- Действие: перевод ---
        transfer = api_manager.user_steps.money_transfer(user, transfer_request)

        # --- Проверка: ответ API ---
        assert transfer.fromAccountIdBalance == expected_sender_balance, (
            f"Баланс отправителя в ответе на перевод {transfer.fromAccountIdBalance}, "
            f"ожидали {expected_sender_balance}"
        )

        # --- Проверка: выписка по счёту ---
        sender_after = api_manager.user_steps.get_account(user, funded_account.id)
        transfers_out = find_transactions_by_type(sender_after.transactions, "transfer_out")
        assert len(transfers_out) == 1, (
            f"Операций transfer_out в истории отправителя {funded_account.id} в API {len(transfers_out)}, "
            f"ожидали 1: {transfers_out}"
        )

        receiver_after = api_manager.user_steps.get_account(user, second_account.id)
        transfers_in = find_transactions_by_type(receiver_after.transactions, "transfer_in")
        assert len(transfers_in) == 1, (
            f"Операций transfer_in в истории получателя {second_account.id} в API {len(transfers_in)}, "
            f"ожидали 1: {transfers_in}"
        )

        # --- Проверка: база данных ---
        sender_from_db = AccountCrudDb.get_account_by_id(db_session, funded_account.id)
        assert sender_from_db is not None, f"Счёт отправителя {funded_account.id} не найден в БД"
        assert sender_from_db.balance == expected_sender_balance, (
            f"Баланс отправителя в БД {sender_from_db.balance}, ожидали {expected_sender_balance}"
        )

        receiver_from_db = AccountCrudDb.get_account_by_id(db_session, second_account.id)
        assert receiver_from_db is not None, f"Счёт получателя {second_account.id} не найден в БД"
        assert receiver_from_db.balance == expected_receiver_balance, (
            f"Баланс получателя в БД {receiver_from_db.balance}, ожидали {expected_receiver_balance}"
        )

    @pytest.mark.parametrize("amount", [500.0, 501.0, 5000.0, 9999.0, 10000.0])
    def test_transfer_money_valid(self, api_manager: ApiManager, user: CreateUserRequest,
                                  max_funded_account: AccountDepositResponse, second_account: CreateAccountResponse,
                                  amount: float) -> None:
        # --- Подготовка: перевод суммы на границе лимита; у отправителя 18000 ---
        transfer_request = MoneyTransferRequest(
            fromAccountId=max_funded_account.id,
            toAccountId=second_account.id,
            amount=amount,
        )
        expected_sender_balance = max_funded_account.balance - transfer_request.amount
        expected_receiver_balance = second_account.balance + transfer_request.amount

        # --- Действие: перевод на границах лимита ---
        transfer = api_manager.user_steps.money_transfer(user, transfer_request)

        # --- Проверка: ответ API ---
        assert transfer.fromAccountIdBalance == expected_sender_balance, (
            f"Баланс отправителя в ответе на перевод {transfer.fromAccountIdBalance}, "
            f"ожидали {expected_sender_balance}"
        )

        receiver_after = api_manager.user_steps.get_account(user, second_account.id)
        assert receiver_after.balance == expected_receiver_balance, (
            f"Баланс получателя в API {receiver_after.balance}, ожидали {expected_receiver_balance}"
        )

    @pytest.mark.parametrize("amount", [250.0, 499.0, 10001.0, 15000.0])
    def test_transfer_money_invalid(self, api_manager: ApiManager, user: CreateUserRequest,
                                    max_funded_account: AccountDepositResponse, second_account: CreateAccountResponse,
                                    amount: float, db_session: Session) -> None:
        # --- Подготовка: перевод вне лимита; у отправителя 18000 — отказ только из-за лимита ---
        transfer_request = MoneyTransferRequest(
            fromAccountId=max_funded_account.id,
            toAccountId=second_account.id,
            amount=amount,
        )
        # балансы в БД до перевода — после отказа сравним с ними
        sender_balance_before_db = AccountCrudDb.get_account_by_id(db_session, max_funded_account.id).balance
        receiver_balance_before_db = AccountCrudDb.get_account_by_id(db_session, second_account.id).balance

        # --- Действие: перевод вне лимита ---
        transfer = api_manager.user_steps.money_transfer_out_of_limit(user, transfer_request)

        # --- Проверка: ответ API ---
        # текст ответа немного отличается от текста в Swagger
        assert "Amount must be between 500 and 10000" in transfer.text, (
            f"В ответе нет ошибки о лимите перевода: {transfer.text}"
        )

        # --- Проверка: база данных ---
        db_session.expire_all()  # иначе сессия вернёт балансы, прочитанные до перевода
        sender_from_db = AccountCrudDb.get_account_by_id(db_session, max_funded_account.id)
        assert sender_from_db is not None, (
            f"Счёт отправителя {max_funded_account.id} не найден в БД"
        )
        assert sender_from_db.balance == sender_balance_before_db, (
            f"Баланс отправителя в БД {sender_from_db.balance}, "
            f"ожидали {sender_balance_before_db}"
        )

        receiver_from_db = AccountCrudDb.get_account_by_id(db_session, second_account.id)
        assert receiver_from_db is not None, (
            f"Счёт получателя {second_account.id} не найден в БД"
        )
        assert receiver_from_db.balance == receiver_balance_before_db, (
            f"Баланс получателя в БД {receiver_from_db.balance}, "
            f"ожидали {receiver_balance_before_db}"
        )

    def test_transfer_money_insufficient_funds(self, api_manager: ApiManager, user: CreateUserRequest,
                                               funded_account: AccountDepositResponse,
                                               second_account: CreateAccountResponse) -> None:
        # --- Подготовка: перевод на 0.1 больше, чем есть у отправителя ---
        transfer_request = MoneyTransferRequest(
            fromAccountId=funded_account.id,
            toAccountId=second_account.id,
            amount=funded_account.balance + 0.1,
        )
        expected_sender_balance = funded_account.balance  # перевод отклонён — баланс не меняется

        # --- Действие: перевод без достаточных средств ---
        transfer = api_manager.user_steps.money_transfer_invalid(user, transfer_request)

        # --- Проверка: ответ API ---
        assert "Insufficient funds" in transfer.text, (
            f"В ответе нет ошибки о нехватке денег: {transfer.text}"
        )

        sender_after = api_manager.user_steps.get_account(user, funded_account.id)
        assert sender_after.balance == expected_sender_balance, (
            f"Баланс отправителя в API {sender_after.balance}, ожидали {expected_sender_balance} - "
            f"перевод отклонён, баланс не должен был измениться"
        )
