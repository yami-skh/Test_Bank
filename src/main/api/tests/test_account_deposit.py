import pytest
import requests
import random

# Каждый раз придумывает новое имя: «user» + случайное число.
# По сути, без этого при повторном запуске сервер ответит 409 — такой пользователь уже есть.
def generate_username():
    return "user"+ str(random.randint(0,999999))



# Тесты на пополнение счёта (deposit).
class TestAccountDeposit:
    # ПОЗИТИВНЫЙ тест: пополняем на 1000 — это в пределах 1000–9000, должно пройти.
    def test_account_deposit_valid(self):
        # Имя генерируем ОДИН раз: им создаём пользователя и им же потом входим.
        username = generate_username()
        # 1. Входим админом и забираем его токен — только админ может создавать пользователей.
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


        # 2. Админ создаёт нового пользователя. В заголовке — токен АДМИНА.
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

        # 3. Входим новым пользователем и забираем уже ЕГО токен.
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

        # Дальше всё делаем от имени пользователя — переменная token теперь хранит ЕГО токен.
        token = auth_user_response.json().get("token")

        # 4. Пользователь создаёт счёт. Новый счёт пустой — баланс 0.
        # id счёта берём из ответа на создание счёта.
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

        # 5. Пополняем этот счёт на 1000.
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
        # Пополнение прошло (200), и на счёте теперь 1000.
        assert user_account_deposit_response.status_code == 200
        assert user_account_deposit_response.json().get("balance") == 1000.0

    # НЕГАТИВНЫЙ тест: пополняем на 10000 — это больше лимита 9000, сервер должен отказать.
    def test_account_deposit_invalid(self):
        # Подготовка такая же: админ → новый пользователь → его токен → счёт.
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

        # Пытаемся пополнить на 10000 — больше максимума.
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

        # 400 — сервер отказал: сумма вне лимита 1000–9000.
        assert user_account_deposit_response.status_code == 400








