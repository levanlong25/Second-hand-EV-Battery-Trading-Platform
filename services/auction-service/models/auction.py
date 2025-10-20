from app import db
from datetime import datetime, timezone

class Auction(db.Model):
    __tablename__ = 'auctions'

    auction_id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.listing_id'), nullable=False, unique=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    current_bid = db.Column(db.Numeric(10, 2), nullable=False)
    winning_bidder_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)

    listing = db.relationship('Listing', back_populates='auction')
    winning_bidder = db.relationship('User')

    @property
    def status(self):
        """Tự động tính toán trạng thái của phiên đấu giá."""
        now = datetime.now(timezone.utc)
        if now < self.start_time:
            return "Sắp diễn ra"
        elif self.start_time <= now <= self.end_time:
            return "Đang diễn ra"
        else:
            return "Đã kết thúc"

    def __repr__(self):
        return f"<Auction ID: {self.auction_id}>"