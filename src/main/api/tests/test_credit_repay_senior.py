import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.credit_repay_request import CreditRepayRequest
from src.main.api.models.money_transfer_response import MoneyTransferResponse
from src.main.api.models.user_credit_response import UserCreditResponse
from src.main.db.crud.account_crud import AccountCrudDb
from src.main.db.crud.credit_crud import CreditCrudDb
from src.main.api.utils import find_credits_by_id
from src.main.db.crud.transaction_crud import TransactionCrudDb


@pytest.mark.api
class TestCreditRepay:
    def test_credit_repay(self, api_manager: ApiManager, credit_user: CreateUserRequest,
                          credit_account: CreateAccountResponse, credit: UserCreditResponse,
                          db_session: Session) -> None:
        # --- Подготовка: полное погашение выданного кредита ---
        repay_request = CreditRepayRequest(
            creditId=credit.creditId,
            accountId=credit_account.id,
            amount=credit.amount,
        )
        expected_debt = -credit.amount + repay_request.amount

        # --- Действие: полное погашение ---
        repay_response = api_manager.user_steps.credit_repay(credit_user, repay_request)

        # --- Проверка: ответ API ---
        assert repay_response.amountDeposited == repay_request.amount, (
            f"Сумма погашения в ответе {repay_response.amountDeposited}, ожидали {repay_request.amount}"
        )

        # --- Проверка: база данных ---
        credit_from_db = CreditCrudDb.get_credit_by_id(db_session, credit.creditId)
        assert credit_from_db is not None, (
            f"Кредит {credit.creditId} в БД не найден"
        )
        assert credit_from_db.balance == expected_debt, (
            f"Долг по кредиту в БД {credit_from_db.balance}, ожидали {expected_debt}"
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
    def test_credit_repay_invalid(self, api_manager: ApiManager, credit_user: CreateUserRequest,
                                  credit_account: CreateAccountResponse, funded_credit: UserCreditResponse,
                                  offset: float, error_text: str) -> None:
        # --- Подготовка: погашение неверной суммой; деньги с запасом — отказ только из-за суммы ---
        repay_request = CreditRepayRequest(
            creditId=funded_credit.creditId,
            accountId=credit_account.id,
            amount=funded_credit.amount + offset,
        )
        expected_debt = -funded_credit.amount  # погашение отклонено — долг не меняется

        # --- Действие: погашение неверной суммой ---
        repay_response = api_manager.user_steps.credit_repay_invalid(credit_user, repay_request)

        # --- Проверка: ответ API ---
        assert error_text in repay_response.text, (
            f"В ответе нет ошибки «{error_text}»: {repay_response.text}"
        )

        credit_history = api_manager.user_steps.get_credit_history(credit_user)
        credits = find_credits_by_id(credit_history.credits, funded_credit.creditId)
        assert len(credits) == 1, (
            f"Кредитов {funded_credit.creditId} в истории API {len(credits)}, ожидали 1: {credits}"
        )
        assert credits[0].balance == expected_debt, (
            f"Долг по кредиту в истории API {credits[0].balance}, ожидали {expected_debt} - "
            f"погашение отклонено, долг не должен был измениться"
        )

    def test_credit_repay_insufficient_funds(self, api_manager: ApiManager,
                                             credit_user: CreateUserRequest, credit_account: CreateAccountResponse,
                                             credit: UserCreditResponse, spent_credit: MoneyTransferResponse) -> None:
        # --- Подготовка: полное погашение, но половина денег ушла на другой счёт ---
        repay_request = CreditRepayRequest(
            creditId=credit.creditId,
            accountId=credit_account.id,
            amount=credit.amount,
        )
        expected_debt = -credit.amount  # погашение отклонено — долг не меняется

        # --- Действие: погашение без достаточных средств ---
        repay_response = api_manager.user_steps.credit_repay_invalid(credit_user, repay_request)

        # --- Проверка: ответ API ---
        assert "Insufficient funds" in repay_response.text, (
            f"В ответе нет ошибки о нехватке денег: {repay_response.text}"
        )

        credit_history = api_manager.user_steps.get_credit_history(credit_user)
        credits = find_credits_by_id(credit_history.credits, credit.creditId)
        assert len(credits) == 1, (
            f"Кредитов {credit.creditId} в истории API {len(credits)}, ожидали 1: {credits}"
        )
        assert credits[0].balance == expected_debt, (
            f"Долг по кредиту в истории API {credits[0].balance}, ожидали {expected_debt} - "
            f"погашение отклонено, долг не должен был измениться"
        )

    # Перед тестом делает первое погашение кредита
    @pytest.mark.usefixtures("repaid_credit")
    def test_credit_repay_twice(self, api_manager: ApiManager,
                                credit_user: CreateUserRequest, credit_account: CreateAccountResponse,
                                funded_credit: UserCreditResponse, db_session: Session) -> None:
        # --- Подготовка: повторное погашение; на счёте 18000 — отказ не из-за нехватки денег ---
        repay_request = CreditRepayRequest(
            creditId=funded_credit.creditId,
            accountId=credit_account.id,
            amount=funded_credit.amount,
        )
        expected_balance = funded_credit.balance - funded_credit.amount  # второго списания быть не должно

        # --- Действие: повторное погашение ---
        repay_response = api_manager.user_steps.credit_repay_already_repaid(credit_user, repay_request)

        # --- Проверка: ответ API ---
        assert "already been repaid" in repay_response.text, (
            f"В ответе нет ошибки о погашенном кредите: {repay_response.text}"
        )

        # --- Проверка: база данных ---
        account_from_db = AccountCrudDb.get_account_by_id(db_session, credit_account.id)
        assert account_from_db is not None, (
            f"Счёт {credit_account.id} не найден в БД"
        )
        assert account_from_db.balance == expected_balance, (
            f"Баланс счёта в БД {account_from_db.balance}, ожидали {expected_balance} - "
            f"деньги списались второй раз"
        )

        repayments_from_db = TransactionCrudDb.get_repayments(db_session, credit_id=funded_credit.creditId)
        assert len(repayments_from_db) == 1, (
            f"Погашений кредита {funded_credit.creditId} в БД {len(repayments_from_db)}, "
            f"ожидали 1 - повторное погашение не должно записываться: {repayments_from_db}"
        )
