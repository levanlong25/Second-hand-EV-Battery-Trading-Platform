from app import db

class Fee(db.Model):
    __tablename__ = "fee"

    fee_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.transaction_id', ondelete='CASCADE'), nullable=False)
    percentage = db.Column(db.Float, nullable=False) # pin: 0.05 = 5%, xe 0,1 = 10%
    amount = db.Column(db.Float, nullable=False) # = percentage * final_price
    paid_to_admin = db.Column(db.Boolean, default=False, nullable=False) 

    transaction = db.relationship('Transaction', back_populates='fee')

    def __repr__(self):
        return f"<Fee {self.fee_id} - Transaction {self.transaction_id} - Type {self.fee_type} - Amount {self.amount}>"