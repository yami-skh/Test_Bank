from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey

from src.main.db.base import Base


class Transaction(Base):
    __tablename__ = "transaction"
    id = Column(Integer, primary_key=True, autoincrement=True)
    to_account_id = Column(Integer, ForeignKey("account.id"))
    from_account_id = Column(Integer, ForeignKey("account.id"))
    credit_id = Column(Integer, ForeignKey("credit.id"))
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(20), nullable=False)
    created_at = Column(DateTime, nullable=False)

    def __repr__(self):
        return (f"Transaction(id={self.id}, to_account_id={self.to_account_id}, "
                f"from_account_id={self.from_account_id}, credit_id={self.credit_id}, "
                f"amount={self.amount}, transaction_type={self.transaction_type}, "
                f"created_at={self.created_at})")
