from app import db
from models.listing import Listing
from services.vehicle_service import VehicleService
from services.battery_service import BatteryService

class ListingService:
    @staticmethod
    def get_all_listings():
        lists = Listing.query.all()
        if lists is None:
            return {"error": "No listings found"}
        return lists

    @staticmethod
    def get_listing_by_id(listing_id):
        list =  Listing.query.get(listing_id)
        if not list:
            return {"error": "Listing not exists"}
        return list
    
    @staticmethod
    def get_listings_by_type(listing_type):
        lists = Listing.query.filter_by(type=listing_type).all()
        if lists is None:
            return {"error": "No listings found for this type"}
        return lists
    
    @staticmethod
    def get_listings_by_vehicle_id(vehicle_id):
        lists = Listing.query.filter_by(vehicle_id=vehicle_id).all()
        if lists is None:
            return {"error": "No listings found for this vehicle"}
        return lists
    
    @staticmethod
    def get_listings_by_battery_id(battery_id):
        lists = Listing.query.filter_by(battery_id=battery_id).all()
        if lists is None:
            return {"error": "No listings found for this battery"}
        return lists

    @staticmethod
    def get_listings_by_seller(seller_id):
        lists = Listing.query.filter_by(seller_id=seller_id).all()
        if lists is None:
            return {"error": "No listings found for this seller"}
        return lists

    @staticmethod
    def create_listing(vehicle_id, battery_id, seller_id, type, title, description, price, status='available', ai_suggested_price=None, is_verified=False):
        if type == 'vehicle':
            if not vehicle_id:
                return {"error": "vehicle_id is required for type 'vehicle'"}            
            vehicle = VehicleService.get_vehicle_by_id(vehicle_id)
            if "error" in vehicle:
                return {"error": f"Vehicle with id {vehicle_id} not found"}
            battery_id = None
        elif type == 'battery':
            if not battery_id:
                return {"error": "battery_id is required for type 'battery'"}
                
            battery = BatteryService.get_battery_by_id(battery_id)
            if "error" in battery:
                return {"error": f"Battery with id {battery_id} not found"}
            vehicle_id = None            
        else:
            return {"error": "Invalid listing type specified. Must be 'vehicle' or 'battery'."}
        new_listing = Listing(
            vehicle_id=vehicle_id,
            battery_id=battery_id, 
            seller_id=seller_id,
            type=type,
            title=title,
            description=description,
            price=price,
            status=status,
            ai_suggested_price=ai_suggested_price,
            is_verified=is_verified
        )
        
        db.session.add(new_listing)
        db.session.commit()
        
        return {"message": "Listing created successfully", "listing_id": new_listing.listing_id}

        

    @staticmethod
    def update_listing(listing_id, new_title = None, new_description = None, new_price = None, new_status = None):
        list = Listing.query.get(listing_id)
        if not list:
            return {"error": "Listing not exists"}
        if new_title != None:
            list.title = new_title
        if new_description != None:
            list.description = new_description
        if new_price != None:
            list.price = new_price
        if new_status != None:
            list.status = new_status
        db.session.commit()
        return {"message": "Listing updated successfully"}
        
    @staticmethod
    def delete_listing(listing_id):
        """Xóa một listing"""
        listing = Listing.query.get(listing_id)
        if not listing:
            return {"error": "Listing not exists"}

        db.session.delete(listing)
        db.session.commit()
        return {{"message": "Listing deleted successfully"}}