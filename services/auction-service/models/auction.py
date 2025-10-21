from app import db
from datetime import datetime, timezone

class Auction(db.Model):
    __tablename__ = 'auctions'

    auction_id = db.Column(db.Integer, primary_key=True)
    bidder_id = db.Column(db.Integer, nullable=False)
    battery_id = db.Column(db.Integer, nullable = True)
    vehicle_id = db.Column(db.Integer, nullable=True)
    auction_type = db.Column(db.Enum('vehicle', 'battery', name='auction_type_enum'), nullable=False)
    auction_status = db.Column(
        db.Enum('pending', 'prepare','started', 'ended', 'rejected', name='auction_status_enum'), 
        nullable=False, 
        default='pending'
    )
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    current_bid = db.Column(db.Numeric(10, 2), nullable=False)
    winning_bidder_id = db.Column(db.Integer, nullable=True)