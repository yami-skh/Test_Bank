from dataclasses import dataclass
from enum import Enum
from typing import Type, Optional

from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.account_deposit_response import AccountDepositResponse
from src.main.api.models.account_transactions_response import AccountTransactionsResponse
from src.main.api.models.base_model import BaseModel
from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.models.credit_history_response import CreditHistoryResponse
from src.main.api.models.credit_repay_request import CreditRepayRequest
from src.main.api.models.credit_repay_response import CreditRepayResponse
from src.main.api.models.money_transfer_request import MoneyTransferRequest
from src.main.api.models.money_transfer_response import MoneyTransferResponse
from src.main.api.models.user_credit_request import UserCreditRequest
from src.main.api.models.user_credit_response import UserCreditResponse


@dataclass
class EndpointConfiguration:
    url: str
    request_model: Optional[Type[BaseModel]] = None
    response_model: Optional[Type[BaseModel]] = None


class Endpoint(Enum):
    ADMIN_CREATE_USER = EndpointConfiguration(
        request_model=CreateUserRequest,
        url="/admin/create",
        response_model=CreateUserResponse
    )

    ADMIN_DELETE_USER = EndpointConfiguration(
        url="/admin/users",
    )

    CREATE_USER_ACCOUNT = EndpointConfiguration(
        url="/account/create",
        response_model=CreateAccountResponse
    )

    ACCOUNT_DEPOSIT = EndpointConfiguration(
        request_model=AccountDepositRequest,
        url="/account/deposit",
        response_model=AccountDepositResponse
    )

    MONEY_TRANSFER = EndpointConfiguration(
        request_model=MoneyTransferRequest,
        url="/account/transfer",
        response_model=MoneyTransferResponse
    )

    USER_CREDIT = EndpointConfiguration(
        request_model=UserCreditRequest,
        url="/credit/request",
        response_model=UserCreditResponse
    )

    CREDIT_REPAY = EndpointConfiguration(
        request_model=CreditRepayRequest,
        url="/credit/repay",
        response_model=CreditRepayResponse
    )

    ACCOUNT_TRANSACTIONS = EndpointConfiguration(
        url="/account/transactions",
        response_model=AccountTransactionsResponse
    )

    CREDIT_HISTORY = EndpointConfiguration(
        url="/credit/history",
        response_model=CreditHistoryResponse
    )
