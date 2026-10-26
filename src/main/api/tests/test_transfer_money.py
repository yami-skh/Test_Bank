import requests
import pytest
import random

def generate_user():
    return "user"+ str(random.randint(0,9999999999))

class TestTransferMoney:
    def test_transfer_money_valid(self):
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
        token = auth_admin_response.json().get("token")
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
        user_token = auth_user_response.json().get("token")
        assert auth_user_response.status_code == 200

        create_user_account_response1 = requests.post(
            url="http://localhost:4111/api/account/create",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {user_token}"
            }

        )
        assert create_user_account_response1.status_code == 201
        id_account1 = create_user_account_response1.json().get("id")

        create_user_account_deposit_response = requests.post(
            url="http://localhost:4111/api/account/deposit",
            json={
                "accountId": id_account1,
                "amount": 5000.0
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {user_token}"
            }

        )
        assert create_user_account_deposit_response.status_code == 200

        create_user_account_response2 = requests.post(
            url="http://localhost:4111/api/account/create",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {user_token}"
            }

        )
        assert create_user_account_response2.status_code == 201
        id_account2 = create_user_account_response2.json().get("id")


        transfer_money_response = requests.post(
            url="http://localhost:4111/api/account/transfer",
            json={
                "fromAccountId": id_account1,
                "toAccountId": id_account2,
                "amount": 2000.56
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {user_token}"
            }
        )
        assert transfer_money_response.status_code == 200
        assert transfer_money_response.json().get("fromAccountIdBalance") == 2999.44


    def test_transfer_money_invalid(self):
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
        token = auth_admin_response.json().get("token")
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
        user_token = auth_user_response.json().get("token")
        assert auth_user_response.status_code == 200

        create_user_account_response1 = requests.post(
            url="http://localhost:4111/api/account/create",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {user_token}"
            }

        )
        assert create_user_account_response1.status_code == 201
        id_account1 = create_user_account_response1.json().get("id")

        create_user_account_deposit_response = requests.post(
            url="http://localhost:4111/api/account/deposit",
            json={
                "accountId": id_account1,
                "amount": 5000.0
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {user_token}"
            }

        )
        assert create_user_account_deposit_response.status_code == 200

        create_user_account_response2 = requests.post(
            url="http://localhost:4111/api/account/create",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {user_token}"
            }

        )
        assert create_user_account_response2.status_code == 201
        id_account2 = create_user_account_response2.json().get("id")


        transfer_money_response = requests.post(
            url="http://localhost:4111/api/account/transfer",
            json={
                "fromAccountId": id_account1,
                "toAccountId": id_account2,
                "amount": 6000
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {user_token}"
            }
        )
        assert transfer_money_response.status_code == 422
        # assert transfer_money_response.json().get("fromAccountIdBalance") == 2999.44













