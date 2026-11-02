from src.main.api.models.base_model import BaseModel


class UserCreditRequest(BaseModel):
    accountId: int
    amount: int
    termMonths: int