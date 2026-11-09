import pytest

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