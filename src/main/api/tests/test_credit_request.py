import requests
import pytest
import random


def generate_user():
    return "user" + str(random.randint(0, 9999999999))


class TestCreditRequest:
    def test_credit_request_valid(self):
        username = generate_user()
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
                "Authorization": f"Bearer {admin_token}"
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
        user_token = auth_user_response.json().get("token")
        assert auth_user_response.status_code == 200

        create_user_account_response = requests.post(
            url="http://localhost:4111/api/account/create",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {user_token}"
            }

        )
        assert create_user_account_response.status_code == 201
        id_account = create_user_account_response.json().get("id")

        create_user_credit_response = requests.post(
            url="http://localhost:4111/api/credit/request",
            json={
                "accountId": id_account,
                "amount": 7000,
                "termMonths": 12
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {user_token}"
            }

        )

        assert create_user_credit_response.status_code == 201

        create_user_account_response = requests.get(
            url=f"http://localhost:4111/api/account/transactions/{id_account}",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {user_token}"
            }
        )

        assert create_user_account_response.json().get("balance") == 7000

    def test_credit_request_invalid(self):
        username = generate_user()
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

        admin_token = auth_admin_response.json().get("token")
        assert auth_admin_response.status_code == 200

        create_user_response = requests.post(
            url="http://localhost:4111/api/admin/create",
            json={
                "username": username,
                "password": "Pas!w0rd",
                "role": "ROLE_USER"

            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {admin_token}"
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
        user_token = auth_user_response.json().get("token")
        assert auth_user_response.status_code == 200

        create_user_account_response = requests.post(
            url="http://localhost:4111/api/account/create",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {user_token}"
            }

        )
        assert create_user_account_response.status_code == 201
        id_account = create_user_account_response.json().get("id")

        create_user_credit_response = requests.post(
            url="http://localhost:4111/api/credit/request",
            json={
                "accountId": id_account,
                "amount": 7000,
                "termMonths": 12
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {user_token}"
            }
        )

        assert create_user_credit_response.status_code == 403
