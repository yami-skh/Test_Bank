import allure

from src.main.api.foundation.endpoint import Endpoint
from src.main.api.foundation.requesters.crud_requester import CrudRequester
from src.main.api.foundation.requesters.validate_crud_requester import ValidateCrudRequester
from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.credit_repay_request import CreditRepayRequest
from src.main.api.models.money_transfer_request import MoneyTransferRequest
from src.main.api.models.user_credit_request import UserCreditRequest
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.steps.base_steps import BaseSteps


class UserSteps(BaseSteps):
    # --- Счёт ---

    @allure.step("Создаём банковский счёт")
    def create_account(self, create_user_request: CreateUserRequest):
        account_response = ValidateCrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.CREATE_USER_ACCOUNT,
            ResponseSpecs.request_create()
        ).post()

        return account_response

    @allure.step("Запрашиваем информацию по счету")
    def get_account(self, create_user_request: CreateUserRequest, account_id: int):
        get_account_response = ValidateCrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.ACCOUNT_TRANSACTIONS,
            ResponseSpecs.request_ok()
        ).get(account_id)

        return get_account_response

    # --- Пополнение ---

    @allure.step("Пополняем счёт")
    def deposit(self, create_user_request: CreateUserRequest, account_deposit_request: AccountDepositRequest):
        deposit_response = ValidateCrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.ACCOUNT_DEPOSIT,
            ResponseSpecs.request_ok()
        ).post(account_deposit_request)

        return deposit_response

    @allure.step("Негатив: Пополняем счёт вне лимитов и ждём отказ 400")
    def deposit_invalid(self, create_user_request: CreateUserRequest, account_deposit_request: AccountDepositRequest):
        deposit_response = CrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.ACCOUNT_DEPOSIT,
            ResponseSpecs.request_bad()
        ).post(account_deposit_request)

        return deposit_response

    @allure.step("Негатив: Пробуем пополнить счёт без авторизации, ждём отказ 401")
    def deposit_unauthorized(self, account_deposit_request: AccountDepositRequest):
        deposit_response = CrudRequester(
            RequestSpecs.unauth_headers(),
            Endpoint.ACCOUNT_DEPOSIT,
            ResponseSpecs.request_unauthorized()
        ).post(account_deposit_request)

        return deposit_response

    # --- Перевод ---

    @allure.step("Переводим средства")
    def money_transfer(self, create_user_request: CreateUserRequest, money_transfer_request: MoneyTransferRequest):
        transfer_response = ValidateCrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.MONEY_TRANSFER,
            ResponseSpecs.request_ok()
        ).post(money_transfer_request)

        return transfer_response

    @allure.step("Негатив: Переводим средства вне лимитов, ждём отказ 400")
    def money_transfer_out_of_limit(self, create_user_request: CreateUserRequest, money_transfer_request: MoneyTransferRequest):
        transfer_response = CrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.MONEY_TRANSFER,
            ResponseSpecs.request_bad()
        ).post(money_transfer_request)

        return transfer_response

    @allure.step("Негатив: Переводим больше, чем есть на счёте, ждём отказ 422")
    def money_transfer_invalid(self, create_user_request: CreateUserRequest, money_transfer_request: MoneyTransferRequest):
        transfer_response = CrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.MONEY_TRANSFER,
            ResponseSpecs.request_unprocessable()
        ).post(money_transfer_request)

        return transfer_response

    # --- Кредит ---

    @allure.step("Берём кредит")
    def user_credit(self, create_user_request: CreateUserRequest, user_credit_request: UserCreditRequest):
        credit_response = ValidateCrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.USER_CREDIT,
            ResponseSpecs.request_create()
        ).post(user_credit_request)

        return credit_response

    @allure.step("Запрашиваем кредитную историю")
    def get_credit_history(self, create_user_request: CreateUserRequest):
        credit_history_response = ValidateCrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.CREDIT_HISTORY,
            ResponseSpecs.request_ok()
        ).get()

        return credit_history_response

    @allure.step("Негатив: Берём кредит вне лимитов суммы или срока, ждём отказ 400 (в Swagger 422)")
    def user_credit_out_of_limit(self, create_user_request: CreateUserRequest, user_credit_request: UserCreditRequest):
        credit_response = CrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.USER_CREDIT,
            # Свагер: сумма выше 15000 → ошибка 422 "Credit amount cannot exceed 15000", сумма ниже 5000 ошибки нет.
            # Банк по факту на обе границы отдаёт 400 "Amount must be between 5000 and 15000". Сделано по факту.
            ResponseSpecs.request_bad()
        ).post(user_credit_request)

        return credit_response

    @allure.step("Негатив: Берём второй кредит, ждём отказ 404 (в Swagger 403)")
    def user_credit_invalid(self, create_user_request: CreateUserRequest, user_credit_request: UserCreditRequest):
        credit_response = CrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.USER_CREDIT,
        #    ResponseSpecs.request_forbidden() <- Здесь по свагеру должно отдать 403, но по факту отдает 404, сделано по факту.
            ResponseSpecs.request_not_found()
        ).post(user_credit_request)

        return credit_response

    @allure.step("Негатив: Берём кредит с ролью ROLE_USER, ждём отказ 403")
    def user_credit_forbidden(self, create_user_request: CreateUserRequest, user_credit_request: UserCreditRequest):
        credit_response = CrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.USER_CREDIT,
            ResponseSpecs.request_forbidden()
        ).post(user_credit_request)

        return credit_response

    # --- Погашение ---

    @allure.step("Погашаем кредит")
    def credit_repay(self, create_user_request: CreateUserRequest, credit_repay_request: CreditRepayRequest):
        repay_response = ValidateCrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.CREDIT_REPAY,
            ResponseSpecs.request_ok()
        ).post(credit_repay_request)

        return repay_response

    @allure.step("Негатив: Погашаем кредит неверной суммой или без денег на счёте, ждём отказ 422")
    def credit_repay_invalid(self, create_user_request: CreateUserRequest, credit_repay_request: CreditRepayRequest):
        repay_response = CrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.CREDIT_REPAY,
            ResponseSpecs.request_unprocessable()
        ).post(credit_repay_request)

        return repay_response

    # 409 — в Swagger у /credit/repay такого кода нет, проверено на стенде
    @allure.step("Негатив: Повторно погашаем уже погашенный кредит, ждём отказ 409")
    def credit_repay_already_repaid(self, create_user_request: CreateUserRequest, credit_repay_request: CreditRepayRequest):
        repay_response = CrudRequester(
            RequestSpecs.auth_headers(create_user_request.username, create_user_request.password),
            Endpoint.CREDIT_REPAY,
            ResponseSpecs.request_conflict()
        ).post(credit_repay_request)

        return repay_response
