from app import db
from datetime import datetime, timezone

class Contract(db.Model):
    __tablename__ = "contract"

    contract_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.transaction_id', ondelete='CASCADE'), nullable=False)
    term = db.Column(db.Text, nullable=False) # Điều khoản hợp đồng
    signed_by_seller = db.Column(db.Boolean, default=False, nullable=False)
    signed_by_buyer = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default = lambda: datetime.now(timezone.utc), nullable=False)

    transaction = db.relationship('Transaction', back_populates='contract')

    def __repr__(self):
        return (f"<Contract {self.contract_id} - Transaction {self.transaction_id} "
            f"- SellerSigned={self.signed_by_seller} - BuyerSigned={self.signed_by_buyer}>")
