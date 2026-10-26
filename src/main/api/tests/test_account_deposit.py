import pytest
import requests
import random

def generate_username():
    return "user"+ str(random.randint(0,999999))



class TestAccountDeposit:
    def test_account_deposit_valid(self):
        username = generate_username()
        create_admin_response = requests.post(
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
        token = create_admin_response.json().get("token")
        assert create_admin_response.status_code == 200


        create_user_response = requests.post(
            url="http://localhost:4111/api/admin/create",
            json={
                "username": username,
                "password": "Pas!w0rd",
                "role": "ROLE_USER"
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
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
        # assert auth_user_response.json()["user"]["username"] == "yam95"
        # assert auth_user_response.json()["user"]["role"] == "ROLE_USER"

        token = auth_user_response.json().get("token")

        create_account_user_response = requests.post(
            url="http://localhost:4111/api/account/create",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
        )
        assert create_account_user_response.status_code == 201
        assert create_account_user_response.json().get("balance") == 0
        id_account = create_account_user_response.json().get("id")

        user_account_deposit_response = requests.post(
            url="http://localhost:4111/api/account/deposit",
            json={
                "accountId": id_account,
                "amount": 1000.0
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }

        )
        assert user_account_deposit_response.status_code == 200
        assert user_account_deposit_response.json().get("balance") == 1000.0

    def test_account_deposit_invalid(self):
        username = generate_username()
        create_admin_response = requests.post(
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
        token = create_admin_response.json().get("token")
        assert create_admin_response.status_code == 200

        create_user_response = requests.post(
            url="http://localhost:4111/api/admin/create",
            json={
                "username": username,
                "password": "Pas!w0rd",
                "role": "ROLE_USER"
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
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
        # assert auth_user_response.json()["user"]["username"] == "yam95"
        # assert auth_user_response.json()["user"]["role"] == "ROLE_USER"

        token = auth_user_response.json().get("token")

        create_account_user_response = requests.post(
            url="http://localhost:4111/api/account/create",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
        )
        assert create_account_user_response.status_code == 201
        assert create_account_user_response.json().get("balance") == 0
        id_account = create_account_user_response.json().get("id")

        user_account_deposit_response = requests.post(
            url="http://localhost:4111/api/account/deposit",
            json={
                "accountId": id_account,
                "amount": 10000.0
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }

        )

        assert user_account_deposit_response.status_code == 400








