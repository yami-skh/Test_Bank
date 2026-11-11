from typing import Callable, Dict

import json

import allure
import requests
from requests import Response

from src.main.api.configs.config import Config
from src.main.api.foundation.endpoint import Endpoint


class HttpRequester:
    def __init__(self, request_spec: Dict[str, str], endpoint: Endpoint, response_spec: Callable[[Response], None]):
        self.request_spec = request_spec
        self.endpoint = endpoint
        self.response_spec = response_spec

    def _request(self, method, model=None, path_suffix=None):
        url = f"{Config.fetch('backendUrl')}{self.endpoint.value.url}"
        if path_suffix is not None:
            url = f"{url}/{path_suffix}"
        body = model.model_dump() if model is not None else None
        with allure.step(f"{method} {url}"):
            if body is not None:
                allure.attach(json.dumps(body, indent=2, ensure_ascii=False),
                              name="Запрос",
                              attachment_type=allure.attachment_type.JSON)
            response = requests.request(
                method=method,
                url=url,
                headers=self.request_spec,
                json=body,
            )
            allure.attach(response.text, name="Ответ", attachment_type=allure.attachment_type.JSON)
            self.response_spec(response)
            return response
