from typing import Callable, Dict

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
        response = requests.request(
            method=method,
            url=url,
            headers=self.request_spec,
            json=body,
        )
        self.response_spec(response)
        return response
