import pytest
import requests
import random


def user_generate():
    return "user" + str(random.randint(0,99999999))

@pytest.mark.api
class TestCreditRepay:
    def test_credit_repay_valid(self):
        username = user_generate()
        auth_admin_response = requests.post(
            url="http://localhost:4111/api/auth/token/login",
            json={
                "username": "admin",
                "password": "123456"
            },
            headers={
                "Content-Type": "application/json",
                "accept": "application/json"
            }
        )

        assert auth_admin_response.status_code == 200
        admin_token = auth_admin_response.json().get("token")

        create_user_response = requests.post(
            url="http://localhost:4111/api/admin/create",
            json={
                "username": username,
                "password": "Pas!w0rd",
                "role": "ROLE_CREDIT_SECRET"
            },
            headers={
                "Content-Type": "application/json",
                "authorization": f"Bearer {admin_token}",
            }
        )

        assert create_user_response.status_code == 200


        auth_user_response = requests.post(
            url="http://localhost:4111/api/auth/token/login",
            json={
                "username": username,
                "password": "Pas!w0rd"
            },
            headers={
                "Content-Type": "application/json",
                "accept": "application/json"
            }
        )

        assert auth_user_response.status_code == 200
        user_token = auth_user_response.json().get("token")

        create_account_response = requests.post(
            url="http://localhost:4111/api/account/create",
            headers={
                "Content-Type": "application/json",
                "authorization": f"Bearer {user_token}",
            }

        )

        assert create_account_response.status_code == 201
        id_account = create_account_response.json().get("id")

        credit_request_response = requests.post(
            url="http://localhost:4111/api/credit/request",
            json={
                "accountId": id_account,
                "amount": 10000,
                "termMonths": 15

            },
            headers={
                "Content-Type": "application/json",
                "authorization": f"Bearer {user_token}",
            }
        )

        assert credit_request_response.status_code == 201
        credit_id = credit_request_response.json().get("creditId")

        credit_repay_response = requests.post(
            url="http://localhost:4111/api/credit/repay",
            json={
                "accountId": id_account,
                "creditId": credit_id,
                "amount": 10000,

            },
            headers={
                "Content-Type": "application/json",
                "accept": "application/json",
                "authorization": f"Bearer {user_token}"
            }
        )

        assert credit_repay_response.status_code == 200


    def test_credit_repay_invalid(self):
        username = user_generate()
        auth_admin_response = requests.post(
            url="http://localhost:4111/api/auth/token/login",
            json={
                "username": "admin",
                "password": "123456"
            },
            headers={
                "Content-Type": "application/json",
                "accept": "application/json"
            }
        )

        assert auth_admin_response.status_code == 200
        admin_token = auth_admin_response.json().get("token")

        create_user_response = requests.post(
            url="http://localhost:4111/api/admin/create",
            json={
                "username": username,
                "password": "Pas!w0rd",
                "role": "ROLE_CREDIT_SECRET"
            },
            headers={
                "Content-Type": "application/json",
                "authorization": f"Bearer {admin_token}",
            }
        )

        assert create_user_response.status_code == 200

        auth_user_response = requests.post(
            url="http://localhost:4111/api/auth/token/login",
            json={
                "username": username,
                "password": "Pas!w0rd"
            },
            headers={
                "Content-Type": "application/json",
                "accept": "application/json"
            }
        )

        assert auth_user_response.status_code == 200
        user_token = auth_user_response.json().get("token")

        create_account_response = requests.post(
            url="http://localhost:4111/api/account/create",
            headers={
                "Content-Type": "application/json",
                "authorization": f"Bearer {user_token}",
            }

        )

        assert create_account_response.status_code == 201
        id_account = create_account_response.json().get("id")

        credit_request_response = requests.post(
            url="http://localhost:4111/api/credit/request",
            json={
                "accountId": id_account,
                "amount": 10000,
                "termMonths": 15

            },
            headers={
                "Content-Type": "application/json",
                "authorization": f"Bearer {user_token}",
            }
        )

        assert credit_request_response.status_code == 201
        credit_id = credit_request_response.json().get("creditId")

        credit_repay_response = requests.post(
            url="http://localhost:4111/api/credit/repay",
            json={
                "accountId": id_account,
                "creditId": credit_id,
                "amount": 12000,

            },
            headers={
                "Content-Type": "application/json",
                "accept": "application/json",
                "authorization": f"Bearer {user_token}"
            }
        )

        assert credit_repay_response.status_code == 422


