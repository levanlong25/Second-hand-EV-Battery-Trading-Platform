from app import db
from models.battery import Battery
from models.listing import Listing
from services.listing_service import ListingService

class BatteryService:
    @staticmethod
    def addBattery(listing_id, capacity_kwh, health_percent, manufacturer):
        battery = Battery(
            listing_id=listing_id,
            capacity_kwh=capacity_kwh,
            health_percent=health_percent,
            manufacturer=manufacturer
        )
        db.session.add(battery)
        db.session.commit()

    @staticmethod
    def updateBatteryStatus(battery_id, capacity_kwh=None, health_percent=None):
        """Cập nhật dung lượng hoặc tình trạng pin"""
        battery = Battery.query.get(battery_id)
        if not battery:
            return {"error": "Battery not found"}

        if capacity_kwh is not None:
            battery.capacity_kwh = capacity_kwh
        if health_percent is not None:
            battery.health_percent = health_percent
        db.session.commit()
        return {"message": "Battery updated successfully"}
    @staticmethod
    def get_all_batteries():
        """Lấy danh sách tất cả pin"""
        batteries = Battery.query.all()
        if not batteries:
            return {"error": "No batteries found"}
        return batteries

    @staticmethod
    def get_battery_by_id(battery_id):
        """Lấy thông tin pin theo ID"""
        battery = Battery.query.get(battery_id)
        if not battery:
            return {"error": "Battery not found"}
        return battery

    @staticmethod
    def delete_battery(battery_id):
        """Xóa pin theo ID"""
        battery = Battery.query.get(battery_id)
        if not battery:
            return {"error": "Battery not found"}

        db.session.delete(battery)
        db.session.commit()
        return {"message": "Battery deleted successfully"}
    
    @staticmethod
    def get_batteries_by_user_id(user_id):
        """Lấy danh sách pin theo user_id"""
        batteries = Battery.query.filter_by(user_id=user_id).all()
        if not batteries:
            return {"error": "No batteries found for this user"}
        return batteries
    
    @staticmethod
    def post_battery_to_listing(battery_id, seller_id, type, title, description, price):
        battery = Battery.query.get(battery_id)
        if not battery:
            return {"error": "Battery not found"}
        seller_id = battery.user_id
        type = 'battery'
        new_listing = Listing(
            item_id=battery_id,
            seller_id=seller_id,
            type=type,
            title=title,
            description=description,
            price=price
        )
        db.session.add(new_listing)
        db.session.commit()
        return {"message": "Battery listed successfully", "listing_id": new_listing.listing_id}
    
    @staticmethod
    def remove_battery_from_listing(battery_id):
        battery = Battery.query.get(battery_id)
        if not battery:
            return {"error": "Battery not found"}
        listing = ListingService.get_listings_by_battery_id(battery_id)
        if "error" in listing:
            return {"error": "Listing not found for this battery"}
        listing = listing.listing_id
        result = ListingService.delete_listing(listing)
        if "error" in result:
            return result["error"]
        return result["message"]
    
    @staticmethod
    def update_battery_listing(battery_id, new_title=None, new_description=None, new_price=None, new_status=None):
        battery = Battery.query.get(battery_id)
        if not battery:
            return {"error": "Battery not found"}
        listing = ListingService.get_listings_by_battery_id(battery_id)
        if "error" in listing:
            return {"error": "Listing not found for this battery"}
        listing = listing.listing_id
        result = ListingService.update_listing(listing, new_title=new_title, new_description=new_description, new_price=new_price, new_status=new_status)
        if "error" in result:
            return result["error"]
        return result["message"]