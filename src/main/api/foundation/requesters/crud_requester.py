from typing import Optional

from requests import Response

from src.main.api.foundation.http_requester import HttpRequester
from src.main.api.models.base_model import BaseModel


class CrudRequester(HttpRequester):
    def post(self, model: Optional[BaseModel] = None) -> Response:
        return self._request("POST", model)

    def delete(self, user_id: int) -> Response:
        return self._request("DELETE", path_suffix=user_id)

    def get(self, object_id: Optional[int] = None) -> Response:
        return self._request("GET", path_suffix=object_id)
