from app import db  

class VehicleSaleData(db.Model):
    """Lưu trữ dữ liệu lịch sử bán XE"""
    __tablename__ = 'vehicle_sale_data'
    
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50), nullable=False, index=True) 
    model = db.Column(db.String(50), nullable=False, index=True)  
    year = db.Column(db.Integer, nullable=False)
    mileage = db.Column(db.Integer, nullable=False)
    sale_price = db.Column(db.Float, nullable=False)  

    def to_dict(self):
        return {
            'id': self.id,
            'type': 'vehicle',
            'brand': self.brand,
            'model': self.model,
            'year': self.year,
            'mileage': self.mileage,
            'sale_price': self.sale_price
        }

class BatterySaleData(db.Model):
    """Lưu trữ dữ liệu lịch sử bán PIN"""
    __tablename__ = 'battery_sale_data'
    
    id = db.Column(db.Integer, primary_key=True)
    manufacturer = db.Column(db.String(50), nullable=False, index=True)  
    capacity_kwh = db.Column(db.Float, nullable=False)
    health_percent = db.Column(db.Float, nullable=False)
    sale_price = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'type': 'battery',
            'manufacturer': self.manufacturer,
            'capacity_kwh': self.capacity_kwh,
            'health_percent': self.health_percent,
            'sale_price': self.sale_price
        }