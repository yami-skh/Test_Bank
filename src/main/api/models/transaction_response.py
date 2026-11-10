from typing import Optional

from src.main.api.models.base_model import BaseModel


class TransactionResponse(BaseModel):
    transactionId: int
    type: str
    amount: float
    fromAccountId: Optional[int] = None
    toAccountId: Optional[int] = None
    createdAt: str
    creditId: Optional[int] = None
