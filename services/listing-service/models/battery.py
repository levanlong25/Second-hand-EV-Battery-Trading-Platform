from app import db

class Battery(db.Model):
    __tablename__ = 'batteries'

    battery_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False) 
    capacity_kwh = db.Column(db.Float, nullable=False)
    health_percent = db.Column(db.Float, nullable=False)
    manufacturer = db.Column(db.String(50), nullable=False)

    listing = db.relationship('Listing', back_populates='battery', uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Battery {self.battery_id} - {self.manufacturer}, {self.capacity_kwh}kWh>'