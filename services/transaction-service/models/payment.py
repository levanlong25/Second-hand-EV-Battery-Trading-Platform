from app import db
from datetime import datetime, timezone

class Payment(db.Model):
    __tablename__ = "payment"

    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.transaction_id', ondelete='CASCADE'), nullable=False)
    payment_method = db.Column(db.Enum('e-wallet', 'cash', 'bank', name='payment_method_enum'), nullable=False)
    amount = db.Column(db.Float, nullable=False) # = final_price - fee
    payment_status = db.Column(db.Enum('initiated', 'pending', 'completed', 'failed', name='payment_status_enum'), default='initiated', nullable=False)
    # completed = paid, failed = deleted transaction, initiated = awaiting_payment
    created_at = db.Column(db.DateTime, default = lambda: datetime.now(timezone.utc), nullable=False)

    transaction = db.relationship('Transaction', back_populates='payment')

    def __repr__(self):
        return f"<Payment {self.payment_id} - Transaction {self.transaction_id} - Method {self.payment_method} - Status {self.payment_status}>"