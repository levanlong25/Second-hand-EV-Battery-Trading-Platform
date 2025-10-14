from app import db

class Contract(db.Model):
    __tablename__ = "contract"

    contract_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.transaction_id'), nullable=False)
    term = db.Column(db.Text, nullable=False) # Điều khoản hợp đồng
    signed_by_seller = db.Column(db.Boolean, default=False, nullable=False)
    signed_by_buyer = db.Column(db.Boolean, default=False, nullable=False)

    transaction = db.relationship('Transaction', back_populates='contract')

    def __repr__(self):
        return f"<Contract {self.contract_id} - Transaction {self.transaction_id} - Signed {self.signed}>"