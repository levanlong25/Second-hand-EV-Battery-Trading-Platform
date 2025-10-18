from app import db
from models.listing import Listing
from models.vehicle import Vehicle
from models.battery import Battery
from models.listing_image import ListingImage
from models.report import Report
from models.watchlist import WatchList
import traceback

class ListingService:
    # --- CORE LISTING FUNCTIONS ---
    @staticmethod
    def create_listing(seller_id, listing_type, data, vehicle_id=None, battery_id=None):
        """
        Tạo một tin đăng mới cho một vehicle hoặc battery đã tồn tại.
        """
        required_fields = ['title', 'description', 'price']
        if not all(field in data for field in required_fields):
            return None, "Missing title, description, or price."

        try:
            if listing_type == 'vehicle':
                item_to_list = Vehicle.query.get(vehicle_id)
                if not item_to_list or item_to_list.user_id != seller_id:
                    return None, "Vehicle not found or you don't own it."
                # SỬA LỖI: Kiểm tra mối quan hệ 'listing' thay vì thuộc tính 'listing_id'
                if item_to_list.listing:
                    return None, "This vehicle is already listed for sale."

            elif listing_type == 'battery':
                item_to_list = Battery.query.get(battery_id)
                if not item_to_list or item_to_list.user_id != seller_id:
                    return None, "Battery not found or you don't own it."
                # SỬA LỖI: Kiểm tra mối quan hệ 'listing'
                if item_to_list.listing:
                    return None, "This battery is already listed for sale."
            else:
                return None, "Invalid listing type."

            new_listing = Listing(
                seller_id=seller_id,
                listing_type=listing_type,
                title=data['title'],
                description=data['description'],
                price=data['price'],
                vehicle_id=vehicle_id,
                battery_id=battery_id,
                status='pending'
            )
            db.session.add(new_listing)
            db.session.commit()
            
            return new_listing, "Listing created successfully, awaiting approval."
        except Exception as e:
            db.session.rollback()
            traceback.print_exc() # In lỗi chi tiết ra log
            return None, f"An internal error occurred: {str(e)}"

    @staticmethod
    def delete_listing(listing_id, user_id, user_role):
        """Xóa một tin đăng."""
        listing = Listing.query.get(listing_id)
        if not listing:
            return False, "Listing not found."

        if listing.seller_id != user_id and user_role != 'admin':
            return False, "You don't have permission to delete this listing."

        try:
            # SQLAlchemy tự động xử lý việc ngắt kết nối quan hệ.
            # Không cần gán listing.vehicle.listing_id = None nữa.
            db.session.delete(listing)
            db.session.commit()
            return True, "Listing removed successfully."
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            return False, f"An error occurred: {str(e)}"
    
    @staticmethod
    def update_listing(listing_id, user_id, data):
        """Cập nhật thông tin của một tin đăng."""
        listing = Listing.query.get(listing_id)
        if not listing or listing.seller_id != user_id:
            return None, "Listing not found or you don't have permission to edit it."

        listing.title = data.get('title', listing.title)
        listing.description = data.get('description', listing.description)
        listing.price = data.get('price', listing.price)
        
        db.session.commit()
        return listing, "Listing updated successfully."

    # --- SEARCH & GET LISTING FUNCTIONS ---
    @staticmethod
    def get_all_listings():
        """Lấy tất cả tin đăng đã được duyệt (công khai)."""
        return Listing.query.filter(Listing.status == 'available').order_by(Listing.created_at.desc()).all()

    @staticmethod
    def get_listing_by_id(listing_id):
        return Listing.query.get(listing_id)
    
    @staticmethod
    def get_listing_by_vehicle_id(vehicle_id):
        return Listing.query.filter_by(vehicle_id=vehicle_id).first()

    @staticmethod
    def get_listing_by_battery_id(battery_id):
        return Listing.query.filter_by(battery_id=battery_id).first()
    
    @staticmethod
    def get_listings_by_seller(seller_id):
        return Listing.query.filter_by(seller_id=seller_id).order_by(Listing.created_at.desc()).all()

    # --- ADMIN FUNCTIONS ---
    @staticmethod
    def get_pending_listings():
        """(Admin) Lấy các tin đăng đang chờ duyệt."""
        return Listing.query.filter_by(status='pending').order_by(Listing.created_at.asc()).all()
    
    @staticmethod
    def update_listing_status(listing_id, new_status):
        """(Admin) Cập nhật trạng thái của tin đăng."""
        listing = Listing.query.get(listing_id)
        if not listing: return None, "Listing not found."
        
        allowed_statuses = ['available', 'sold', 'pending', 'rejected']
        if new_status not in allowed_statuses: return None, "Invalid status."
            
        listing.status = new_status
        db.session.commit()
        return listing, "Status updated successfully."

    @staticmethod
    def get_absolutely_all_listings():
        """(Admin) Lấy tất cả tin đăng, không lọc theo trạng thái."""
        return Listing.query.order_by(Listing.created_at.desc()).all()

    # --- WATCHLIST FUNCTIONS ---
    @staticmethod
    def add_to_watchlist(user_id, listing_id):
        listing = Listing.query.get(listing_id)
        if not listing: return None, "Listing not found."
        if user_id == listing.seller_id: return None, "You sell this listing."
        if WatchList.query.filter_by(user_id=user_id, listing_id=listing_id).first():
            return None, "Listing is already in your watchlist."
        
        new_entry = WatchList(user_id=user_id, listing_id=listing_id)
        db.session.add(new_entry)
        db.session.commit()
        return new_entry, "Added to watchlist."

    @staticmethod
    def remove_from_watchlist(watchlist_id):
        entry = WatchList.query.get(watchlist_id)
        if not entry: return False, "Entry not found in your watchlist."
        
        db.session.delete(entry)
        db.session.commit()
        return True, "Removed from watchlist."

    @staticmethod
    def get_watchlist_by_id(watchlist_id):
        return WatchList.query.get(watchlist_id)
    @staticmethod
    def get_watchlist(user_id):
        return [
            ListingService.get_listing_by_id(item.listing_id)
            for item in WatchList.query.filter_by(user_id=user_id).all()
        ]
    # --- REPORT FUNCTIONS ---
    @staticmethod
    def create_report(reporter_id, listing_id, report_type, description):
        if not Listing.query.get(listing_id): return None, "Listing not found."
        
        new_report = Report(reporter_id=reporter_id, listing_id=listing_id, report_type=report_type, description=description)
        db.session.add(new_report)
        db.session.commit()
        return new_report, "Report submitted successfully."
        
    @staticmethod
    def get_reports_by_listing_id(listing_id):
        """(Admin) Lấy tất cả report của một tin đăng."""
        return Report.query.filter_by(listing_id=listing_id).order_by(Report.created_at.desc()).all()