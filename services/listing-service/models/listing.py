from app import db
from datetime import datetime, timezone

class Listing(db.Model):
    __tablename__ = 'listing'
 
    listing_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    seller_id = db.Column(db.Integer, nullable=False)
    battery_id = db.Column(db.Integer, db.ForeignKey('batteries.battery_id'), default = None, nullable=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.vehicle_id'), default = None, nullable=True)
    type = db.Column(db.Enum('vehicle', 'battery', name='listing_type_enum'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    status = db.Column(db.Enum('available', 'sold', 'pending', 'approved', name='listing_status_enum'), default='available')
    ai_suggested_price = db.Column(db.Numeric(precision=10, scale=2), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default= lambda: datetime.now(timezone.utc))
 
    battery = db.relationship('Battery', back_populates='listing', uselist=False)
    image = db.relationship('ListingImage', back_populates='listing', cascade = 'all, delete')
    watchlist = db.relationship("WatchList", back_populates = "listing", cascade = 'all, delete')
    report = db.relationship('Report', back_populates = "listing", cascade = 'all, delete')
    vehicle = db.relationship("Vehicle", back_populates="listing", uselist=False)
 
    def __repr__(self):
        return f"<Listing {self.title} (ID: {self.listing_id})>"