from src.main.api.models.base_model import BaseModel


class CreditResponse(BaseModel):
    creditId: int
    accountId: int
    amount: float
    termMonths: int
    balance: float
    createdAt: str