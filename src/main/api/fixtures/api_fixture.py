from typing import List, Any

import pytest

from src.main.api.classes.api_manager import ApiManager


# Доступ ко всем шагам: admin_steps и user_steps
@pytest.fixture
def api_manager(created_obj: List[Any]) -> ApiManager:
    return ApiManager(created_obj)