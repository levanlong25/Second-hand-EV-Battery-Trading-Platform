from app import db
from datetime import datetime, timezone

class Listing(db.Model):
    __tablename__ = 'listings'

    listing_id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.vehicle_id'), nullable=True, unique=True)
    battery_id = db.Column(db.Integer, db.ForeignKey('batteries.battery_id'), nullable=True, unique=True)
    listing_type = db.Column(db.Enum('vehicle', 'battery', name='listing_type_enum'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum('available', 'sold', 'pending', 'rejected', name='listing_statuses'), default='pending', nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
 
    seller = db.relationship('User', back_populates='listings')
    vehicle = db.relationship('Vehicle', back_populates='listing')
    battery = db.relationship('Battery', back_populates='listing')
     
    images = db.relationship('ListingImage', back_populates='listing', cascade='all, delete-orphan')
    watchlists = db.relationship("WatchList", back_populates="listing", cascade='all, delete-orphan')
    reports = db.relationship('Report', back_populates="listing", cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Listing {self.title} (ID: {self.listing_id})>"

