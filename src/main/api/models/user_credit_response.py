from src.main.api.models.base_model import BaseModel


class UserCreditResponse(BaseModel):
    # В Swagger поле называется accountId, а API на самом деле возвращает id —
    # расхождение документации и реального ответа. Модель сделана по факту.
    id: int
    amount: float
    termMonths: int
    balance: float
    creditId: int