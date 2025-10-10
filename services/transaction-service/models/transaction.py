from app import db
from datetime import datetime, timezone

class Transaction(db.Model):
    __tablename__ = "transaction"

    transaction_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    listing_id = db.Column(db.Integer, nullable = False)
    buyer_id = db.Column(db.Integer, nullable = False)
    seller_id = db.Column(db.Integer, nullable = False)
    final_price = db.Column(db.Float, nullable = False)
    transaction_status = db.Column(db.Enum('pending', 'paid'), default = 'pending', nullable = False)
    create_at = db.Column(db.DataTime, default = lambda: datetime.now(timezone.utc))

    payment = db.relationship('Payment', back_populates='transaction', uselist=False)
    fee = db.relationship('Fee', back_populates='transaction', uselist=False)   
    contract = db.relationship('Contract', back_populates='transaction', uselist=False)

    def __repr__(self):
        return f"<Transaction {self.transaction_id} - Listing {self.listing_id} - Buyer {self.buyer_id} - Seller {self.seller_id} - Status {self.transaction_status}>"