import pytest
from sqlalchemy.orm import Session

from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.credit_repay_request import CreditRepayRequest
from src.main.api.models.money_transfer_request import MoneyTransferRequest
from src.main.api.models.user_credit_request import UserCreditRequest
from src.main.db.crud.account_crud import AccountCrudDb
from src.main.db.crud.credit_crud import CreditCrudDb
from src.main.db.crud.transaction_crud import TransactionCrudDb

MAX_DEPOSIT = 9000.0  # Максимальная сумма пополнения по требованиям проекта


@pytest.mark.api
class TestCreditRepay:
    def test_credit_repay(self, api_manager, create_user_request, db_session: Session):
        # --- Подготовка: пользователь с кредитной ролью и выданный кредит ---
        user = create_user_request(role="ROLE_CREDIT_SECRET")
        account = api_manager.user_steps.create_account(user)

        credit_request = RandomModelGenerator.generate(UserCreditRequest)
        credit_request.accountId = account.id
        credit = api_manager.user_steps.user_credit(user, credit_request)

        repay_request = CreditRepayRequest(
            creditId=credit.creditId,
            accountId=account.id,
            amount=credit.amount,
        )
        expected_balance = credit.balance - repay_request.amount
        expected_debt = -credit.amount + repay_request.amount

        # --- Действие: полное погашение ---
        repay_response = api_manager.user_steps.credit_repay(user, repay_request)

        # --- Проверка: ответ API ---
        assert repay_response.amountDeposited == repay_request.amount, (
            f"Сумма погашения в ответе {repay_response.amountDeposited}, ожидали {repay_request.amount}"
        )
        assert repay_response.creditId == credit.creditId, (
            f"В ответе погашен кредит {repay_response.creditId}, ожидали {credit.creditId}"
        )

        account_after = api_manager.user_steps.get_account(user, account.id)
        assert account_after.balance == expected_balance, (
            f"Баланс счёта в API {account_after.balance}, ожидали {expected_balance}"
        )

        credit_history = api_manager.user_steps.get_credit_history(user)
        credits = [c for c in credit_history.credits if c.creditId == credit.creditId]
        assert len(credits) == 1, (
            f"Кредитов {credit.creditId} в истории API {len(credits)}, ожидали 1: {credits}"
        )
        assert credits[0].balance == expected_debt, (
            f"Долг по кредиту в истории API {credits[0].balance}, ожидали {expected_debt}"
        )

        # --- Проверка: база данных ---
        credit_from_db = CreditCrudDb.get_credit_by_id(db_session, credit.creditId)
        assert credit_from_db is not None, (
            f"Кредит {credit.creditId} в БД не найден"
        )
        assert credit_from_db.balance == expected_debt, (
            f"Долг по кредиту в БД {credit_from_db.balance}, ожидали {expected_debt}"
        )

        account_from_db = AccountCrudDb.get_account_by_id(db_session, account.id)
        assert account_from_db is not None, (
            f"Счёт {account.id} не найден в БД"
        )
        assert account_from_db.balance == expected_balance, (
            f"Баланс счёта в БД {account_from_db.balance}, ожидали {expected_balance}"
        )

        repayments_from_db = TransactionCrudDb.get_repayments(db_session, credit_id=credit.creditId)
        assert len(repayments_from_db) == 1, (
            f"Погашений кредита {credit.creditId} в БД {len(repayments_from_db)}, "
            f"ожидали 1: {repayments_from_db}"
        )

    @pytest.mark.parametrize(
        "offset, error_text",
        [
            (-1.0, "The amount is not enough"),
            (-3000, "The amount is not enough"),
            (1.0, "Repayment amount exceeds remaining debt"),
            (500.0, "Repayment amount exceeds remaining debt"),
        ],
    )
    def test_credit_repay_invalid(self, api_manager, create_user_request, offset, error_text):
        # --- Подготовка: кредит и деньги с запасом — отказ только из-за неверной суммы ---
        user = create_user_request(role="ROLE_CREDIT_SECRET")
        account = api_manager.user_steps.create_account(user)

        deposit_request = RandomModelGenerator.generate(AccountDepositRequest)
        deposit_request.accountId = account.id
        api_manager.user_steps.deposit(user, deposit_request)

        credit_request = RandomModelGenerator.generate(UserCreditRequest)
        credit_request.accountId = account.id
        credit = api_manager.user_steps.user_credit(user, credit_request)

        repay_request = CreditRepayRequest(
            creditId=credit.creditId,
            accountId=account.id,
            amount=credit.amount + offset,
        )
        expected_balance = credit.balance  # погашение отклонено — баланс и долг не меняются
        expected_debt = -credit.amount

        # --- Действие: погашение неверной суммой ---
        repay_response = api_manager.user_steps.credit_repay_invalid(user, repay_request)

        # --- Проверка: ответ API ---
        assert error_text in repay_response.text, (
            f"В ответе нет ошибки «{error_text}»: {repay_response.text}"
        )

        account_after = api_manager.user_steps.get_account(user, account.id)
        assert account_after.balance == expected_balance, (
            f"Баланс счёта в API {account_after.balance}, ожидали {expected_balance} - "
            f"погашение отклонено, баланс не должен был измениться"
        )

        credit_history = api_manager.user_steps.get_credit_history(user)
        credits = [c for c in credit_history.credits if c.creditId == credit.creditId]
        assert len(credits) == 1, (
            f"Кредитов {credit.creditId} в истории API {len(credits)}, ожидали 1: {credits}"
        )
        assert credits[0].balance == expected_debt, (
            f"Долг по кредиту в истории API {credits[0].balance}, ожидали {expected_debt} - "
            f"погашение отклонено, долг не должен был измениться"
        )

    def test_credit_repay_insufficient_funds(self, api_manager, create_user_request):
        # --- Подготовка: кредит, половина денег ушла на другой счёт — на погашение не хватает ---
        user = create_user_request(role="ROLE_CREDIT_SECRET")

        account = api_manager.user_steps.create_account(user)
        other_account = api_manager.user_steps.create_account(user)

        credit_request = RandomModelGenerator.generate(UserCreditRequest)
        credit_request.accountId = account.id
        credit = api_manager.user_steps.user_credit(user, credit_request)

        transfer_request = MoneyTransferRequest(
            fromAccountId=account.id,
            toAccountId=other_account.id,
            amount=credit.amount / 2,
        )
        transfer = api_manager.user_steps.money_transfer(user, transfer_request)

        repay_request = CreditRepayRequest(
            creditId=credit.creditId,
            accountId=account.id,
            amount=credit.amount,
        )
        expected_balance = transfer.fromAccountIdBalance  # погашение отклонено — баланс и долг не меняются
        expected_debt = -credit.amount

        # --- Действие: погашение без достаточных средств ---
        repay_response = api_manager.user_steps.credit_repay_invalid(user, repay_request)

        # --- Проверка: ответ API ---
        assert "Insufficient funds" in repay_response.text, (
            f"В ответе нет ошибки о нехватке денег: {repay_response.text}"
        )

        account_after = api_manager.user_steps.get_account(user, account.id)
        assert account_after.balance == expected_balance, (
            f"Баланс счёта в API {account_after.balance}, ожидали {expected_balance} - "
            f"погашение отклонено, баланс не должен был измениться"
        )

        credit_history = api_manager.user_steps.get_credit_history(user)
        credits = [c for c in credit_history.credits if c.creditId == credit.creditId]
        assert len(credits) == 1, (
            f"Кредитов {credit.creditId} в истории API {len(credits)}, ожидали 1: {credits}"
        )
        assert credits[0].balance == expected_debt, (
            f"Долг по кредиту в истории API {credits[0].balance}, ожидали {expected_debt} - "
            f"погашение отклонено, долг не должен был измениться"
        )

    def test_credit_repay_twice(self, api_manager, create_user_request, db_session: Session):
        # --- Подготовка: кредит уже погашен; на счёте 18000, чтобы отказ был не из-за нехватки денег ---
        user = create_user_request(role="ROLE_CREDIT_SECRET")
        account = api_manager.user_steps.create_account(user)

        deposit_request = AccountDepositRequest(accountId=account.id, amount=MAX_DEPOSIT)
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
        expected_balance = account_after_first.balance  # второго списания быть не должно
        expected_debt = -credit.amount + repay_request.amount

        # --- Действие: повторное погашение ---
        repay_response_second = api_manager.user_steps.credit_repay_already_repaid(user, repay_request)

        # --- Проверка: ответ API ---
        assert "already been repaid" in repay_response_second.text, (
            f"В ответе нет ошибки о погашенном кредите: {repay_response_second.text}"
        )

        account_after_second = api_manager.user_steps.get_account(user, account.id)
        assert account_after_second.balance == expected_balance, (
            f"Баланс счёта в API {account_after_second.balance}, ожидали {expected_balance} - "
            f"деньги списались второй раз"
        )

        credit_history = api_manager.user_steps.get_credit_history(user)
        credits = [c for c in credit_history.credits if c.creditId == credit.creditId]
        assert len(credits) == 1, (
            f"Кредитов {credit.creditId} в истории API {len(credits)}, ожидали 1: {credits}"
        )
        assert credits[0].balance == expected_debt, (
            f"Долг по кредиту в истории API {credits[0].balance}, ожидали {expected_debt} - "
            f"повторное погашение не должно менять долг"
        )

        # --- Проверка: база данных ---
        credit_from_db = CreditCrudDb.get_credit_by_id(db_session, credit_id=credit.creditId)
        assert credit_from_db is not None, (
            f"Кредит {credit.creditId} в БД не найден"
        )
        assert credit_from_db.balance == expected_debt, (
            f"Долг по кредиту в БД {credit_from_db.balance}, ожидали {expected_debt} - "
            f"повторное погашение не должно менять долг"
        )

        account_from_db = AccountCrudDb.get_account_by_id(db_session, account.id)
        assert account_from_db is not None, (
            f"Счёт {account.id} не найден в БД"
        )
        assert account_from_db.balance == expected_balance, (
            f"Баланс счёта в БД {account_from_db.balance}, ожидали {expected_balance} - "
            f"деньги списались второй раз"
        )

        repayments_from_db = TransactionCrudDb.get_repayments(db_session, credit_id=credit.creditId)
        assert len(repayments_from_db) == 1, (
            f"Погашений кредита {credit.creditId} в БД {len(repayments_from_db)}, "
            f"ожидали 1 - повторное погашение не должно записываться: {repayments_from_db}"
        )
