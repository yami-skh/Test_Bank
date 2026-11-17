from http import HTTPStatus
from typing import Callable

from requests import Response


class ResponseSpecs:
    @staticmethod
    def request_ok() -> Callable[[Response], None]:
        def confirm(response: Response) -> None:
            assert response.status_code == HTTPStatus.OK, response.text
        return confirm

    @staticmethod
    def request_create() -> Callable[[Response], None]:
        def confirm(response: Response) -> None:
            assert response.status_code == HTTPStatus.CREATED, response.text
        return confirm

    @staticmethod
    def request_bad() -> Callable[[Response], None]:
        def confirm(response: Response) -> None:
            assert response.status_code == HTTPStatus.BAD_REQUEST, response.text
        return confirm

    @staticmethod
    def request_unprocessable() -> Callable[[Response], None]:
        def confirm(response: Response) -> None:
            assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, response.text
        return confirm

    # проверяю пополнения без токенов
    @staticmethod
    def request_unauthorized() -> Callable[[Response], None]:
        def confirm(response: Response) -> None:
            assert response.status_code == HTTPStatus.UNAUTHORIZED, response.text
        return confirm

    @staticmethod
    def request_forbidden() -> Callable[[Response], None]:
        def confirm(response: Response) -> None:
            assert response.status_code == HTTPStatus.FORBIDDEN, response.text
        return confirm

    @staticmethod
    def request_not_found() -> Callable[[Response], None]:
        def confirm(response: Response) -> None:
            assert response.status_code == HTTPStatus.NOT_FOUND, response.text
        return confirm

    @staticmethod
    def request_conflict() -> Callable[[Response], None]:
        def confirm(response: Response) -> None:
            assert response.status_code == HTTPStatus.CONFLICT, response.text
        return confirm