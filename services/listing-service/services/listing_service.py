from app import db
from models.listing import Listing
from services.vehicle_service import VehicleService
from services.battery_service import BatteryService
from models.listing_image import ListingImage
from models.report import Report
from models.watchlist import WatchList

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
    
    @staticmethod
    def add_image_to_listing(listing_id, image_url):
        listing = Listing.query.get(listing_id)
        if not listing:
            return {"error": "Listing not exists"}
        new_image = ListingImage(
            listing_id=listing_id,
            url=image_url
        )
        db.session.add(new_image)
        db.session.commit()
        return {"message": "Image added to listing successfully", "image_id": new_image.image_id}
    @staticmethod
    def get_images_by_listing_id(listing_id):
        images = ListingImage.query.filter_by(listing_id=listing_id).all()
        if images is None:
            return {"error": "No images found for this listing"}
        return images
    @staticmethod
    def delete_image(image_id):
        image = ListingImage.query.get(image_id)
        if not image:
            return {"error": "Image not exists"}

        db.session.delete(image)
        db.session.commit()
        return {"message": "Image deleted successfully"}
    @staticmethod
    def update_image(image_id, new_url):
        image = ListingImage.query.get(image_id)
        if not image:
            return {"error": "Image not exists"}
        image.url = new_url
        db.session.commit()
        return {"message": "Image updated successfully"}
    @staticmethod
    def verify_listing(listing_id):
        listing = Listing.query.get(listing_id)
        if not listing:
            return {"error": "Listing not exists"}
        listing.is_verified = True
        db.session.commit()
        return {"message": "Listing verified successfully"}
    @staticmethod
    def update_status(listing_id, new_status):
        listing = Listing.query.get(listing_id)
        if not listing:
            return {"error": "Listing not exists"}
        listing.status = new_status
        db.session.commit()
        return {"message": "Listing status updated successfully"}
    @staticmethod
    def suggest_price():
        pass
    @staticmethod
    def create_report(reporter_id, listing_id, report_type):
        listing = Listing.query.get(listing_id)
        if not listing:
            return {"error": "Listing not exists"}
        if report_type not in ['seller', 'transaction', 'listing', 'other']:
            return {"error": "Invalid report type"}
        new_report = Report(
            reporter_id=reporter_id,
            listing_id=listing_id,
            report_type=report_type
        )
        db.session.add(new_report)
        db.session.commit()
        return {"message": "Report created successfully", "report_id": new_report.report_id}
    @staticmethod
    def get_reports_by_listing_id(listing_id):
        reports = Report.query.filter_by(listing_id=listing_id).all()
        if reports is None:
            return {"error": "No reports found for this listing"}
        return reports
    @staticmethod
    def add_to_watchlist(user_id, listing_id):
        listing = Listing.query.get(listing_id)
        if not listing:
            return {"error": "Listing not exists"}
        existing_entry = WatchList.query.filter_by(user_id=user_id, listing_id=listing_id).first()
        if existing_entry:
            return {"error": "Listing already in watchlist"}
        new_watchlist_entry = WatchList(
            user_id=user_id,
            listing_id=listing_id
        )
        db.session.add(new_watchlist_entry)
        db.session.commit()
        return {"message": "Listing added to watchlist successfully", "watchlist_id": new_watchlist_entry.id}
    @staticmethod
    def remove_from_watchlist(user_id, listing_id):
        entry = WatchList.query.filter_by(user_id=user_id, listing_id=listing_id).first()
        if not entry:
            return {"error": "Listing not in watchlist"}
        db.session.delete(entry)
        db.session.commit()
        return {"message": "Listing removed from watchlist successfully"}
    @staticmethod
    def get_watchlist_by_user(user_id):
        entries = WatchList.query.filter_by(user_id=user_id).all()
        if entries is None:
            return {"error": "No watchlist entries found for this user"}
        return entries