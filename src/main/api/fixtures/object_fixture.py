import logging
from typing import List, Any, Generator

import pytest

from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.steps.admin_steps import AdminSteps


# Список созданных пользователей — после теста удаляются
@pytest.fixture
def created_obj() -> Generator[List[Any], None, None]:
    objects: List[Any] = []
    yield objects
    clean_user(objects)

# Чистка
def clean_user(objects: List[Any]) -> None:
    api_manager = AdminSteps(objects)
    for u in objects:
        if isinstance(u, CreateUserResponse):
            api_manager.delete_user(u.id)
        else:
            logging.warning(f"Error in delete user_id: {type(u)}")
