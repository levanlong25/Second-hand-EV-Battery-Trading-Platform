from app import db

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    vehicle_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    mileage = db.Column(db.Integer, nullable=False)

    owner = db.relationship('User', back_populates='vehicles', foreign_keys=[user_id])

    listing = db.relationship("Listing", back_populates="vehicle", uselist=False, cascade="all, delete-orphan")