from src.main.api.models.base_model import BaseModel

class MoneyTransferRequest(BaseModel):
    fromAccountId: int
    toAccountId: int
    amount: float