from sqlalchemy.orm import Session

from src.main.db.models.transaction_table import Transaction


class TransactionCrudDb:
    @staticmethod
    def get_deposits(db: Session, account_id: int) -> list[Transaction]:
        return db.query(Transaction).filter_by(to_account_id=account_id, transaction_type="deposit").all()

    @staticmethod
    def get_transfer(db: Session, from_account_id: int, to_account_id: int) -> Transaction | None:
        return db.query(Transaction).filter_by(from_account_id=from_account_id, to_account_id=to_account_id, transaction_type="transfer").first()