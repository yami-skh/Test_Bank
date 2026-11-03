from typing import List, Any

from src.main.api.specs.request_specs import RequestSpecs


class BaseSteps:
    def __init__(self, created_obj: List[Any]):
        self.created_obj = created_obj
        self.admin_headers = RequestSpecs.auth_headers(username='admin', password='123456')