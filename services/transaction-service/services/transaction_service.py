from models.transaction import Transaction
from app import db

class TransactionService:
    @staticmethod
    def create_transaction(listing_id, buyer_id, seller_id, final_price, transaction_status='pending'):
        new_transaction = Transaction(
            listing_id=listing_id,
            buyer_id=buyer_id,
            seller_id=seller_id,
            final_price=final_price,
            transaction_status=transaction_status
        )
        db.session.add(new_transaction)
        db.session.commit()
        return new_transaction
    @staticmethod
    def update_transaction_status(transaction_id, new_status):
        transaction = Transaction.query.get(transaction_id)
        if transaction:
            transaction.transaction_status = new_status
            db.session.commit()
            return transaction
        return None
    @staticmethod
    def cancel_transaction(transaction_id):
        transaction = Transaction.query.get(transaction_id)
        if transaction:
            db.session.delete(transaction)
            db.session.commit()
            return True
        return False
    @staticmethod
    def get_transaction_by_id(transaction_id):
        return Transaction.query.get(transaction_id)