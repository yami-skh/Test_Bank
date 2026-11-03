import requests
import pytest
import random

# Каждый раз придумывает новое имя: «user» + случайное число.
# По сути, без этого при повторном запуске сервер ответит 409 — такой пользователь уже есть.
def generate_user():
    return "user"+ str(random.randint(0,9999999999))

# Тесты на перевод денег между двумя счетами одного пользователя.
@pytest.mark.api
class TestTransferMoney:
    # ПОЗИТИВНЫЙ тест: обычный перевод, который должен пройти.
    def test_transfer_money_valid(self):
        # Имя генерируем ОДИН раз: им создаём пользователя и им же потом входим.
        username = generate_user()
        # 1. Входим админом и забираем его токен — только админ может создавать пользователей.
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
        # То есть дальше всё делаем от имени пользователя, а не админа.
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

        # 4. Пользователь создаёт первый счёт — с него будем переводить.
        # id счёта берём из ответа на СОЗДАНИЕ счёта (в ответе на логин его нет).
        create_user_account_response1 = requests.post(
            url="http://localhost:4111/api/account/create",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {user_token}"
            }

        )
        assert create_user_account_response1.status_code == 201
        id_account1 = create_user_account_response1.json().get("id")

        # 5. Кладём на первый счёт 5000, чтобы было что переводить.
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

        # 6. Создаём второй счёт — на него будем переводить.
        create_user_account_response2 = requests.post(
            url="http://localhost:4111/api/account/create",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {user_token}"
            }

        )
        assert create_user_account_response2.status_code == 201
        id_account2 = create_user_account_response2.json().get("id")


        # 7. Переводим 2000.56 с первого счёта на второй.
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
        # Перевод прошёл (200), и у отправителя осталось 5000 - 2000.56 = 2999.44.
        assert transfer_money_response.status_code == 200
        assert transfer_money_response.json().get("fromAccountIdBalance") == 2999.44
# Проверка баланса получателя, для проверку удачного перевода
        # GET-запрос к истории второго счёта: id счёта прямо в адресе, тела нет.
        # Из ответа берём balance — сколько реально лежит на счёте получателя.
        receiver_account_response = requests.get(
            url=f"http://localhost:4111/api/account/transactions/{id_account2}",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {user_token}"
            }
        )
        assert receiver_account_response.status_code == 200
        # У получателя было 0, стало 2000.56 — значит, деньги дошли.
        assert receiver_account_response.json().get("balance") == 2000.56


    # НЕГАТИВНЫЙ тест: переводим больше, чем есть на счёте — сервер должен отказать.
    def test_transfer_money_invalid(self):
        # Подготовка такая же, как в позитивном тесте:
        # админ → новый пользователь → его токен → два счёта, на первом 5000.
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


        # Пытаемся перевести 6000, а на счёте только 5000.
        transfer_money_response = requests.post(
            url="http://localhost:4111/api/account/transfer",
            json={
                "fromAccountId": id_account1,
                "toAccountId": id_account2,
                "amount": 6000.0
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {user_token}"
            }
        )
        # 422 — сервер отказал: денег не хватает.
        assert transfer_money_response.status_code == 422















