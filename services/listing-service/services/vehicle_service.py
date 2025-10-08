from models.vehicle import Vehicle
from services.listing_service import ListingService
from app import db

class VehicleService:
    @staticmethod
    def get_vehicle_by_id(vehicle_id):
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return {"error": "Vehicle not exists"}
        return vehicle
    @staticmethod
    def get_vehicles_by_user_id(user_id):
        vehicles = Vehicle.query.filter_by(user_id=user_id).all()
        return vehicles
    
    @staticmethod
    def create_vehicle(user_id, brand, model, year, mileage):
        new_vehicle = Vehicle(
            user_id=user_id,
            brand=brand,
            model=model,
            year=year,
            mileage=mileage
        )
        db.session.add(new_vehicle)
        db.session.commit()
        return {"message": "Vehicle created successfully", "vehicle_id": new_vehicle.vehicle_id}

    @staticmethod
    def update_vehicle(vehicle_id, new_brand=None, new_model=None, new_year=None, new_mileage=None):
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return {"error": "Vehicle not exists"}
        if new_brand is not None:
            vehicle.brand = new_brand
        if new_model is not None:
            vehicle.model = new_model
        if new_year is not None:
            vehicle.year = new_year
        if new_mileage is not None:
            vehicle.mileage = new_mileage
        db.session.commit()
        return {"message": "Vehicle updated successfully"}

    @staticmethod
    def delete_vehicle(vehicle_id):
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return {"error": "Vehicle not exists"}
        db.session.delete(vehicle)
        db.session.commit()
        return {"message": "Vehicle deleted successfully"}