from app import db
from models.auction import Auction
from models.listing import Listing
from datetime import datetime, timezone

class AuctionService:
    @staticmethod
    def get_auction_by_id(auction_id):
        return Auction.query.get(auction_id)

    @staticmethod
    def create_auction(data):
        try:
            new_auction = Auction(**data)
            db.session.add(new_auction)
            db.session.commit()
            return new_auction, "Tạo phiên đấu giá thành công."
        except Exception as e:
            db.session.rollback()
            return None, f"Lỗi server: {str(e)}"

    @staticmethod
    def update_auction(auction, data):
        try:
            auction.start_time = data.get('start_time', auction.start_time)
            auction.end_time = data.get('end_time', auction.end_time)
            db.session.commit()
            return auction, "Cập nhật thành công."
        except Exception as e:
            db.session.rollback()
            return None, f"Lỗi server: {str(e)}"

    @staticmethod
    def delete_auction(auction):
        try:
            db.session.delete(auction)
            db.session.commit()
            return True, "Xóa phiên đấu giá thành công."
        except Exception as e:
            db.session.rollback()
            return False, f"Lỗi server: {str(e)}"

    @staticmethod
    def place_bid(auction, bidder_id, bid_amount):
        try:
            auction.current_bid = bid_amount
            auction.winning_bidder_id = bidder_id
            db.session.commit()
            return auction, "Đặt giá thành công."
        except Exception as e:
            db.session.rollback()
            return None, f"Lỗi server: {str(e)}"

    @staticmethod
    def filter_active_auctions():
        now = datetime.now(timezone.utc)
        return Auction.query.filter(Auction.start_time <= now, Auction.end_time >= now).all()

    @staticmethod
    def filter_auctions_by_type(listing_type):
        return Auction.query.join(Listing).filter(Listing.listing_type == listing_type).all()