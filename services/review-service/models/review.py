from app import db
from datetime import datetime, timezone
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import validates        

class Review(db.Model):
    __tablename__ = 'reviews'
    __table_args__ = (CheckConstraint('rating >= 0 and rating <= 5', name = 'check_rating_range'),)

    review_id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, nullable=False)
    reviewer_id = db.Column(db.Integer, nullable=False)
    reviewed_user_id = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default= lambda: datetime.now(timezone.utc), nullable=False)
        
    @validates('rating')
    def validate_rating(self, key, value):
        if value < 0 or value > 5:
            raise ValueError("Rating must be between 0 and 5")
        return value