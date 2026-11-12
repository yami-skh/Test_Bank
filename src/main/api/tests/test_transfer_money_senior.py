import pytest
from sqlalchemy.orm import Session

from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.money_transfer_request import MoneyTransferRequest
from src.main.db.crud.account_crud import AccountCrudDb
from src.main.db.crud.transaction_crud import TransactionCrudDb

MAX_DEPOSIT = 9000.0  # Максимальная сумма пополнения по требованиям проекта


@pytest.mark.api
class TestTransferMoney:
    def test_transfer_money(self, api_manager, create_user_request, db_session: Session):
        # --- Подготовка: пользователь, два счёта, деньги на счёте отправителя ---
        user = create_user_request()

        sender = api_manager.user_steps.create_account(user)
        receiver = api_manager.user_steps.create_account(user)

        deposit_request = RandomModelGenerator.generate(AccountDepositRequest)
        deposit_request.accountId = sender.id
        deposit = api_manager.user_steps.deposit(user, deposit_request)

        transfer_request = MoneyTransferRequest(
            fromAccountId=sender.id,
            toAccountId=receiver.id,
            amount=deposit.balance / 2,
        )
        expected_sender_balance = deposit.balance - transfer_request.amount
        expected_receiver_balance = receiver.balance + transfer_request.amount

        # --- Действие: перевод ---
        transfer = api_manager.user_steps.money_transfer(user, transfer_request)

        # --- Проверка: ответ API ---
        assert transfer.fromAccountIdBalance == expected_sender_balance

        receiver_after = api_manager.user_steps.get_account(user, receiver.id)
        assert receiver_after.balance == expected_receiver_balance

        # --- Проверка: база данных ---
        sender_from_db = AccountCrudDb.get_account_by_id(db_session, sender.id)
        assert sender_from_db is not None, f"Счёт отправителя {sender.id} не найден в БД"
        assert sender_from_db.balance == expected_sender_balance, (
            f"Баланс отправителя в БД {sender_from_db.balance}, ожидали {expected_sender_balance}"
        )

        receiver_from_db = AccountCrudDb.get_account_by_id(db_session, receiver.id)
        assert receiver_from_db is not None, f"Счёт получателя {receiver.id} не найден в БД"
        assert receiver_from_db.balance == expected_receiver_balance, (
            f"Баланс получателя в БД {receiver_from_db.balance}, ожидали {expected_receiver_balance}"
        )

        transfer_from_db = TransactionCrudDb.get_transfer(
            db_session, from_account_id=sender.id, to_account_id=receiver.id
        )
        assert transfer_from_db is not None, (
            f"Перевод со счёта {sender.id} на счёт {receiver.id} не найден в БД"
        )
        assert transfer_from_db.amount == transfer_request.amount, (
            f"Сумма перевода в БД {transfer_from_db.amount}, ожидали {transfer_request.amount}"
        )

    @pytest.mark.parametrize("amount", [500.0, 501.0, 5000.0, 9999.0, 10000.0])
    def test_transfer_money_valid(self, api_manager, create_user_request, amount):
        # --- Подготовка: два счёта, на счёте отправителя 18000 (с запасом на любую сумму) ---
        user = create_user_request()

        sender = api_manager.user_steps.create_account(user)
        receiver = api_manager.user_steps.create_account(user)

        deposit_request = AccountDepositRequest(accountId=sender.id, amount=MAX_DEPOSIT)
        api_manager.user_steps.deposit(user, deposit_request)
        deposit = api_manager.user_steps.deposit(user, deposit_request)

        transfer_request = MoneyTransferRequest(
            fromAccountId=sender.id,
            toAccountId=receiver.id,
            amount=amount,
        )
        expected_sender_balance = deposit.balance - transfer_request.amount
        expected_receiver_balance = receiver.balance + transfer_request.amount

        # --- Действие: перевод на границах лимита ---
        transfer = api_manager.user_steps.money_transfer(user, transfer_request)

        # --- Проверка: ответ API ---
        assert transfer.fromAccountIdBalance == expected_sender_balance

        receiver_after = api_manager.user_steps.get_account(user, receiver.id)
        assert receiver_after.balance == expected_receiver_balance

    @pytest.mark.parametrize("amount", [250.0, 499.0, 10001.0, 15000.0])
    def test_transfer_money_invalid(self, api_manager, create_user_request, amount):
        # --- Подготовка: два счёта, на счёте отправителя 18000 — отказ только из-за лимита ---
        user = create_user_request()

        sender = api_manager.user_steps.create_account(user)
        receiver = api_manager.user_steps.create_account(user)

        deposit_request = AccountDepositRequest(accountId=sender.id, amount=MAX_DEPOSIT)
        api_manager.user_steps.deposit(user, deposit_request)
        deposit = api_manager.user_steps.deposit(user, deposit_request)

        transfer_request = MoneyTransferRequest(
            fromAccountId=sender.id,
            toAccountId=receiver.id,
            amount=amount,
        )
        expected_sender_balance = deposit.balance      # перевод отклонён — балансы не меняются
        expected_receiver_balance = receiver.balance

        # --- Действие: перевод вне лимита ---
        transfer = api_manager.user_steps.money_transfer_out_of_limit(user, transfer_request)

        # --- Проверка: ответ API ---
        # текст ответа немного отличается от текста в Swagger
        assert "Amount must be between 500 and 10000" in transfer.text

        sender_after = api_manager.user_steps.get_account(user, sender.id)
        assert sender_after.balance == expected_sender_balance

        receiver_after = api_manager.user_steps.get_account(user, receiver.id)
        assert receiver_after.balance == expected_receiver_balance

    def test_transfer_money_insufficient_funds(self, api_manager, create_user_request):
        # --- Подготовка: два счёта, перевод чуть больше, чем есть у отправителя ---
        user = create_user_request()

        sender = api_manager.user_steps.create_account(user)
        receiver = api_manager.user_steps.create_account(user)

        deposit_request = RandomModelGenerator.generate(AccountDepositRequest)
        deposit_request.accountId = sender.id
        deposit = api_manager.user_steps.deposit(user, deposit_request)

        transfer_request = MoneyTransferRequest(
            fromAccountId=sender.id,
            toAccountId=receiver.id,
            amount=deposit.balance + 0.1,
        )
        expected_sender_balance = deposit.balance      # перевод отклонён — балансы не меняются
        expected_receiver_balance = receiver.balance

        # --- Действие: перевод без достаточных средств ---
        transfer = api_manager.user_steps.money_transfer_invalid(user, transfer_request)

        # --- Проверка: ответ API ---
        assert "Insufficient funds" in transfer.text

        sender_after = api_manager.user_steps.get_account(user, sender.id)
        assert sender_after.balance == expected_sender_balance

        receiver_after = api_manager.user_steps.get_account(user, receiver.id)
        assert receiver_after.balance == expected_receiver_balance
