from typing import List

from src.main.api.models.base_model import BaseModel
from src.main.api.models.transaction_response import TransactionResponse


class AccountTransactionsResponse(BaseModel):
    id: int
    number: str
    balance: float
    transactions: List[TransactionResponse]
