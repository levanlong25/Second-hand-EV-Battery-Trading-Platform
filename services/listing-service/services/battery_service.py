from app import db
from models.battery import Battery
from models.listing import Listing

class BatteryService:
    @staticmethod
    def addBattery(listing_id, capacity_kwh, health_percent, manufacturer):
        """Thêm một pin mới vào cơ sở dữ liệu"""
        listing = Listing.query.get(listing_id)
        if not listing:
            return {"error": "Listing not found"}

        battery = Battery(
            listing_id=listing_id,
            capacity_kwh=capacity_kwh,
            health_percent=health_percent,
            manufacturer=manufacturer
        )

        db.session.add(battery)
        try:
            db.session.commit()
            return {"message": "Battery added successfully", "battery_id": battery.battery_id}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {e}"}

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

        try:
            db.session.commit()
            return {"message": "Battery updated successfully"}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {e}"}

    @staticmethod
    def get_all_batteries():
        """Lấy danh sách tất cả pin"""
        batteries = Battery.query.all()
        return [
            {
                "battery_id": b.battery_id,
                "listing_id": b.listing_id,
                "capacity_kwh": b.capacity_kwh,
                "health_percent": b.health_percent,
                "manufacturer": b.manufacturer
            }
            for b in batteries
        ]

    @staticmethod
    def get_battery_by_id(battery_id):
        """Lấy thông tin pin theo ID"""
        battery = Battery.query.get(battery_id)
        if not battery:
            return {"error": "Battery not found"}
        return {
            "battery_id": battery.battery_id,
            "listing_id": battery.listing_id,
            "capacity_kwh": battery.capacity_kwh,
            "health_percent": battery.health_percent,
            "manufacturer": battery.manufacturer
        }

    @staticmethod
    def get_batteries_by_listing(listing_id):
        """Lấy tất cả pin thuộc một listing"""
        batteries = Battery.query.filter_by(listing_id=listing_id).all()
        return [
            {
                "battery_id": b.battery_id,
                "listing_id": b.listing_id,
                "capacity_kwh": b.capacity_kwh,
                "health_percent": b.health_percent,
                "manufacturer": b.manufacturer
            }