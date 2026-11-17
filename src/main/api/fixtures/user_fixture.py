from typing import Callable

import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.generators.model_generator import RandomModelGenerator


# Фабрика: создаёт пользователя через админа с нужной ролью
@pytest.fixture
def create_user_request(api_manager: ApiManager) -> Callable[..., CreateUserRequest]:
    def _create_user(role: str = "ROLE_USER") -> CreateUserRequest:
        user = RandomModelGenerator.generate(CreateUserRequest)
        user.role = role
        api_manager.admin_steps.create_user(user)
        return user

    return _create_user


# Обычный пользователь (ROLE_USER)
@pytest.fixture
def user(create_user_request: Callable[..., CreateUserRequest]) -> CreateUserRequest:
    return create_user_request()


# Пользователь с правом на кредит (ROLE_CREDIT_SECRET)
@pytest.fixture
def credit_user(create_user_request: Callable[..., CreateUserRequest]) -> CreateUserRequest:
    return create_user_request(role="ROLE_CREDIT_SECRET")


# @pytest.fixture
# def account_deposit_request(api_manager):
#     def _create_account(role: str = "ROLE_USER"):
#         user = RandomModelGenerator.generate(AccountDepositRequest)
#         user.role = role
#         api_manager.user_steps.create_account(user)
#         return user
#     return _create_account