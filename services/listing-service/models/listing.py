from app import db
from datetime import datetime

class Listing(db.Model):
    __tablename__ = 'listing'

    listing_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    type = db.Column(db.Enum('product', 'service', 'rental', name='listing_type_enum'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum('available', 'sold', 'pending', 'removed', name='listing_status_enum'), default='available')
    ai_suggested_price = db.Column(db.Float, nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    seller = db.relationship('User', backref=db.backref('listings', lazy=True))

    def __repr__(self):
        return f"<Listing {self.title} (ID: {self.listing_id})>"