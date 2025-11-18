from app import db
from models.battery import Battery
from services.listing_service import ListingService
 
class BatteryService:
    @staticmethod
    def create_battery(user_id, data):
        """
        Thêm một viên pin mới vào kho cá nhân của người dùng.
        Lưu ý: Model 'Battery' của bạn bắt buộc phải có trường 'user_id'.
        """
        # Kiểm tra dữ liệu đầu vào
        required_fields = ['capacity_kwh', 'health_percent', 'manufacturer']
        if not all(field in data for field in required_fields):
            return None, "Missing required battery data."
        if data['health_percent'] > 100:
            return None, "Health percentage cannot be greater than 100 "

        new_battery = Battery(
            user_id=user_id, # Bắt buộc phải có trường này trong model
            capacity_kwh=data['capacity_kwh'],
            health_percent=data['health_percent'],
            manufacturer=data['manufacturer']
        )
        db.session.add(new_battery)
        db.session.commit()
        return new_battery, "Battery created successfully."

    @staticmethod
    def get_battery_by_id(battery_id):
        """Lấy thông tin pin bằng ID."""
        return Battery.query.get(battery_id)

    @staticmethod
    def get_batteries_by_user_id(user_id):
        """Lấy tất cả pin trong kho của người dùng."""
        # Giả định model Battery có trường user_id
        return Battery.query.filter_by(user_id=user_id).order_by(Battery.battery_id.desc()).all()

    @staticmethod
    def update_battery(battery_id, user_id, data):
        """Cập nhật thông tin của một viên pin trong kho (yêu cầu quyền sở hữu)."""
        battery = Battery.query.get(battery_id)
        if not battery or battery.user_id != user_id:
            return None, "Battery not found or you don't have permission to edit it."
        
        battery.capacity_kwh = data.get('capacity_kwh', battery.capacity_kwh)
        battery.health_percent = data.get('health_percent', battery.health_percent)
        battery.manufacturer = data.get('manufacturer', battery.manufacturer)
        
        db.session.commit()
        return battery, "Battery updated successfully."

    @staticmethod
    def delete_battery(battery_id, user_id):
        """Xóa một viên pin khỏi kho (chỉ khi nó không đang được đăng bán)."""
        battery = Battery.query.get(battery_id)
        # Kiểm tra quyền sở hữu
        if not battery or battery.user_id != user_id:
            return False, "Battery not found or you don't have permission to delete it."
        
        # Kiểm tra xem có đang được đăng bán không
        if battery.listing:
            return False, "Cannot delete a battery that is currently listed. Please remove the listing first."
            
        db.session.delete(battery)
        db.session.commit()
        return True, "Battery deleted successfully."

    # --- Các hàm liên quan đến Listing ---

    @staticmethod
    def post_battery_to_listing(user_id, battery_id, data):
        """Đăng bán một viên pin đã có trong kho."""
        listing, message = ListingService.create_listing(
            seller_id=user_id,
            listing_type='battery',
            data=data,
            battery_id=battery_id
        )
        if not listing:
            return None, message  
        return listing, "Battery listed for sale successfully."

    @staticmethod
    def remove_battery_from_listing(user_id, user_role, battery_id):
        """Gỡ một viên pin khỏi sàn giao dịch."""
        listing = ListingService.get_listing_by_battery_id(battery_id)
        if not listing:
            return False, "This battery is not currently listed."
        success, message = ListingService.delete_listing(listing.listing_id, user_id, user_role)
        return success, message