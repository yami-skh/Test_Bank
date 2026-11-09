import pytest

from src.main.api.models.account_deposit_request import AccountDepositRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.generators.model_generator import RandomModelGenerator


@pytest.fixture
def create_user_request(api_manager):
    def _create_user(role: str = "ROLE_USER"):
        user = RandomModelGenerator.generate(CreateUserRequest)
        user.role = role
        api_manager.admin_steps.create_user(user)
        return user

    return _create_user

# @pytest.fixture
# def account_deposit_request(api_manager):
#     def _create_account(role: str = "ROLE_USER"):
#         user = RandomModelGenerator.generate(AccountDepositRequest)
#         user.role = role
#         api_manager.user_steps.create_account(user)
#         return user
#     return _create_account