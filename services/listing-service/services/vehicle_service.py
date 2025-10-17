from app import db
from models.vehicle import Vehicle

class VehicleService:
    @staticmethod
    def create_vehicle(user_id, data):
        """Thêm một chiếc xe mới vào kho cá nhân của người dùng."""
        # Kiểm tra dữ liệu đầu vào
        required_fields = ['brand', 'model', 'year', 'mileage']
        if not all(field in data for field in required_fields):
            return None, "Missing required vehicle data."

        new_vehicle = Vehicle(
            user_id=user_id,
            brand=data['brand'],
            model=data['model'],
            year=data['year'],
            mileage=data['mileage']
        )
        db.session.add(new_vehicle)
        db.session.commit()
        return new_vehicle, "Vehicle created successfully."

    @staticmethod
    def get_vehicle_by_id(vehicle_id):
        """Lấy thông tin xe bằng ID."""
        return Vehicle.query.get(vehicle_id)

    @staticmethod
    def get_vehicles_by_user_id(user_id):
        """Lấy tất cả xe trong kho của người dùng."""
        return Vehicle.query.filter_by(user_id=user_id).order_by(Vehicle.vehicle_id.desc()).all()

    @staticmethod
    def update_vehicle(vehicle_id, user_id, data):
        """Cập nhật thông tin của một chiếc xe trong kho (yêu cầu quyền sở hữu)."""
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle or vehicle.user_id != user_id:
            return None, "Vehicle not found or you don't have permission to edit it."
        
        vehicle.brand = data.get('brand', vehicle.brand)
        vehicle.model = data.get('model', vehicle.model)
        vehicle.year = data.get('year', vehicle.year)
        vehicle.mileage = data.get('mileage', vehicle.mileage)
        
        db.session.commit()
        return vehicle, "Vehicle updated successfully."

    @staticmethod
    def delete_vehicle(vehicle_id, user_id):
        """Xóa một chiếc xe khỏi kho (chỉ khi nó không đang được đăng bán)."""
        vehicle = Vehicle.query.get(vehicle_id)
        # Kiểm tra quyền sở hữu
        if not vehicle or vehicle.user_id != user_id:
            return False, "Vehicle not found or you don't have permission to delete it."
        
        # Kiểm tra xem có đang được đăng bán không
        if vehicle.listing:
            return False, "Cannot delete a vehicle that is currently listed. Please remove the listing first."
            
        db.session.delete(vehicle)
        db.session.commit()
        return True, "Vehicle deleted successfully."
    # --- Các hàm liên quan đến Listing ---

    @staticmethod
    def post_vehicle_to_listing(user_id, vehicle_id, data):
        """Đăng bán một chiếc xe đã có trong kho."""
        from services.listing_service import ListingService
        listing, message = ListingService.create_listing(
            seller_id=user_id,
            listing_type='vehicle',
            data=data,
            vehicle_id=vehicle_id
        )
        if not listing:  
            return None, message
        return listing, "Vehicle listed for sale successfully."

    @staticmethod
    def remove_vehicle_from_listing(user_id, user_role, vehicle_id):
        """Gỡ một chiếc xe khỏi sàn giao dịch."""
        from services.listing_service import ListingService
        listing = ListingService.get_listing_by_vehicle_id(vehicle_id)
        if not listing:
            return False, "This vehicle is not currently listed."
        
        success, message = ListingService.delete_listing(listing.listing_id, user_id, user_role)
        return success, message
