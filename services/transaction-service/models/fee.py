from app import db
from datetime import datetime, timezone

class Fee(db.Model):
    __tablename__ = "fee"

    fee_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.transaction_id', ondelete='CASCADE'), nullable=False)
    fee_type=db.Column(db.Enum('listing', 'auction', name = 'fee_type_enum'), nullable=False)
    product_id=db.Column(db.Integer, nullable = False)
    buyer_id = db.Column(db.Integer, nullable = False) # = người nhấn mua
    seller_id = db.Column(db.Integer, nullable = False) # = người đăng listing
    percentage = db.Column(db.Float, nullable=False) 
    amount = db.Column(db.Float, nullable=False) # = percentage * final_price
    created_at = db.Column(db.DateTime, default = lambda: datetime.now(timezone.utc), nullable=False)

    transaction = db.relationship('Transaction', back_populates='fee')

    def __repr__(self):
        return f"<Fee {self.fee_id} - Transaction {self.transaction_id} - Type {self.fee_type} - Amount {self.amount}>"

