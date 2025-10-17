from models.transaction import Transaction
from models.payment import Payment
from models.fee import Fee
from models.contract import Contract

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
        return new_transaction, "Transaction created successfully."
    @staticmethod
    def create_payment(transaction_id, payment_method, amount, payment_status='initiated'):
        result = TransactionService.get_transaction_by_id(transaction_id = transaction_id)
        if result == None:
            return None, "Transaction not exists"
        if result.transaction_status == 'paid':
            new_payment = Payment(
                transaction_id=transaction_id,
                payment_method=payment_method,
                amount=amount,
                payment_status=payment_status
            )
            db.session.add(new_payment)
            db.session.commit()
            return new_payment, "Payment created successfully."
        return None, "The transaction is currently pending."

    
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