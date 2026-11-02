from src.main.api.models.base_model import BaseModel

class MoneyTransferResponse(BaseModel):
    fromAccountId: int
    toAccountId: int
    fromAccountIdBalance: float