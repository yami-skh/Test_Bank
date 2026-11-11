import logging
from typing import List, Any

import pytest

from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.steps.admin_steps import AdminSteps


@pytest.fixture
def created_obj():
    objects: List[Any] = []
    yield objects
    clean_user(objects)


def clean_user(objects: List[Any]):
    api_manager = AdminSteps(objects)
    for u in objects:
        if isinstance(u, CreateUserResponse):
            api_manager.delete_user(u.id)
        else:
            logging.warning(f"Error in delete user_id: {type(u)}")
