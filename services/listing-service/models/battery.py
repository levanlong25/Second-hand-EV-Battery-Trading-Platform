from app import db

class Battery(db.Model):
    __tablename__ = 'batteries'

    battery_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.listing_id'), nullable=False)
    capacity_kwh = db.Column(db.Float, nullable=False)
    health_percent = db.Column(db.Float, nullable=False)
    manufacturer = db.Column(db.String(50), nullable=False)

    # Quan hệ với bảng listings
    listing = db.relationship('Listing', backref=db.backref('batteries', lazy=True))

    def __repr__(self):
        return f'<Battery {self.battery_id} - {self.manufacturer}, {self.capacity_kwh}kWh>'