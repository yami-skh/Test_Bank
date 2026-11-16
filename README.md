# Test_Bank — API-тесты учебного банка

Автотесты на Python для REST API учебного банка: пополнение, перевод, запрос кредита и погашение.
Проверяются ответ API, последствия через GET (баланс, выписка по счёту, история кредитов) и записи в базе данных.

## Стек

pytest · requests · Pydantic v2 · SQLAlchemy + psycopg2 (PostgreSQL) · rstr (генерация данных) · Allure

## Структура

```
src/main/
├── api/
│   ├── configs/       Config — чтение resources/urls.properties
│   ├── foundation/    Endpoint (ручки и модели), HttpRequester, CrudRequester, ValidateCrudRequester
│   ├── specs/         заголовки запроса и ожидаемые статусы ответа
│   ├── models/        Pydantic-модели запросов и ответов
│   ├── generators/    генератор данных по правилам из моделей
│   ├── steps/         бизнес-шаги админа и пользователя
│   ├── classes/       ApiManager
│   ├── fixtures/      api_manager, пользователь, уборка, db_session
│   └── tests/         тесты
└── db/                engine, модели таблиц, CRUD для проверок в БД
```

Тест читается как сценарий: подготовка → действие → проверка ответа API → проверка выписки → проверка БД.
Созданные пользователи удаляются после теста.

## Запуск

Нужен запущенный стенд банка (Docker): API на `localhost:4111`, PostgreSQL на `localhost:5432`. Адреса — в `resources/urls.properties`.

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m pytest
```

Отчёт Allure (Allure 3, нужен Node.js):

```
python -m pytest --alluredir=allure-results --clean-alluredir
npx.cmd allure awesome allure-results --single-file --output allure-report
```

Отчёт: `allure-report/awesome/index.html`.

## Расхождения со Swagger

Тесты написаны по фактическому поведению стенда, расхождения подписаны в коде шагов и моделей:
- второй кредит — 404 (в Swagger 403);
- кредит вне лимитов — 400 (в Swagger 422);
- повторное погашение — 409 (в Swagger такого кода нет);
- в ответе на кредит поле `id` вместо `accountId`.
