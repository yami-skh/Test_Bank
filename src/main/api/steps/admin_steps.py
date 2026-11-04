from src.main.api.foundation.endpoint import Endpoint
from src.main.api.foundation.requesters.crud_requester import CrudRequester
from src.main.api.foundation.requesters.validate_crud_requester import ValidateCrudRequester
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.steps.base_steps import BaseSteps


class AdminSteps(BaseSteps):
    def create_user(self, create_user_request: CreateUserRequest):
        user_response = ValidateCrudRequester(
            self.admin_headers,
            Endpoint.ADMIN_CREATE_USER,
            ResponseSpecs.request_ok(),
        ).post(create_user_request)

        self.created_obj.append(user_response)
        return user_response

    def delete_user(self, user_id: int):
        CrudRequester(
            self.admin_headers,
            Endpoint.ADMIN_DELETE_USER,
            ResponseSpecs.request_ok(),
        ).delete(user_id)

    def create_invalid_user(self, create_user_request: CreateUserRequest):
        invalid_user_response = CrudRequester(
            self.admin_headers,
            Endpoint.ADMIN_CREATE_USER,
            ResponseSpecs.request_bad(),
        ).post(create_user_request)

        return invalid_user_response