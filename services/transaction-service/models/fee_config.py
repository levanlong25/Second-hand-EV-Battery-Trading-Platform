from app import db
from sqlalchemy import CheckConstraint

class FeeConfig(db.Model):
    __tablename__ = 'fee_config'
    
    id = db.Column(db.Integer, primary_key=True, default=1)
    listing_fee_rate = db.Column(db.Float, nullable=False, default=0.025)
    auction_fee_rate = db.Column(db.Float, nullable=False, default=0.05)
    
    __table_args__ = (CheckConstraint('id = 1', name='singleton_id_check'),)

    def __repr__(self):
        return f"<FeeConfig Rates: Listing={self.listing_fee_rate}, Auction={self.auction_fee_rate}>"

    def to_dict(self):
        return {
            'listing_fee_rate': self.listing_fee_rate,
            'auction_fee_rate': self.auction_fee_rate
        }

