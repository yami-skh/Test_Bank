from typing import List

from src.main.api.models.credit_response import CreditResponse
from src.main.api.models.transaction_response import TransactionResponse


def find_credits_by_id(credits: List[CreditResponse], credit_id: int) -> List[CreditResponse]:
    return [c for c in credits if c.creditId == credit_id]


def find_transactions_by_type(transactions: List[TransactionResponse],
                              transaction_type: str) -> List[TransactionResponse]:
    return [t for t in transactions if t.type == transaction_type]
