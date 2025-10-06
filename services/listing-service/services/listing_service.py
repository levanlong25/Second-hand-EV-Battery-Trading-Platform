from app import db
from models.listing import Listing

class ListingService:
    """
    Service xử lý các nghiệp vụ liên quan đến Listing
    Bao gồm: tạo mới, cập nhật, xóa, lấy danh sách...
    """

    @staticmethod
    def get_all_listings():
        """Lấy tất cả các listing"""
        return Listing.query.all()

    @staticmethod
    def get_listing_by_id(listing_id):
        """Lấy thông tin listing theo ID"""
        return Listing.query.get(listing_id)

    @staticmethod
    def get_listings_by_seller(seller_id):
        """Lấy tất cả listing của 1 người bán"""
        return Listing.query.filter_by(seller_id=seller_id).all()

    @staticmethod
    def create_listing(data):
        """Tạo mới một listing"""
        try:
            new_listing = Listing(
                seller_id=data.get('seller_id'),
                type=data.get('type'),
                title=data.get('title'),
                description=data.get('description'),
                price=data.get('price'),
                status=data.get('status', 'available'),
                ai_suggested_price=data.get('ai_suggested_price'),
                is_verified=data.get('is_verified', False)
            )

            db.session.add(new_listing)
            db.session.commit()
            return new_listing

        except Exception as e:
            db.session.rollback()
            print(f"Lỗi khi tạo listing: {e}")
            return None

    @staticmethod
    def update_listing(listing_id, data):
        """Cập nhật thông tin listing"""
        listing = Listing.query.get(listing_id)
        if not listing:
            return None

        try:
            listing.type = data.get('type', listing.type)
            listing.title = data.get('title', listing.title)
            listing.description = data.get('description', listing.description)
            listing.price = data.get('price', listing.price)
            listing.status = data.get('status', listing.status)
            listing.ai_suggested_price = data.get('ai_suggested_price', listing.ai_suggested_price)
            listing.is_verified = data.get('is_verified', listing.is_verified)

            db.session.commit()
            return listing

        except Exception as e:
            db.session.rollback()
            print(f"Lỗi khi cập nhật listing {listing_id}: {e}")
            return None

    @staticmethod
    def delete_listing(listing_id):
        """Xóa một listing"""
        listing = Listing.query.get(listing_id)
        if not listing:
            return None

        try:
            db.session.delete(listing)
            db.session.commit()
            return True

        except Exception as e:
            db.session.rollback()
            print(f"Lỗi khi xóa listing {listing_id}: {e}")
            return False