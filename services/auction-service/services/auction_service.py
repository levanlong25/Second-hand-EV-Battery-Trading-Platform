from datetime import datetime, timezone, timedelta
from dateutil import parser
import sys, traceback
from sqlalchemy import or_, and_
from app import db
from models.auction import Auction
import logging

logger = logging.getLogger(__name__)

def to_utc(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class AuctionService:
    @staticmethod
    def add_auction(data): 
        required_fields = ['bidder_id', 'auction_type', 'start_time', 'current_bid']
        if not all(field in data for field in required_fields):
            return None, "Missing required fields."

        try: 
            if data.get('auction_type') == 'vehicle':
                if not data.get('vehicle_id'):
                    return None, "Auction type 'vehicle' requires a vehicle_id."
                if Auction.query.filter_by(vehicle_id=data['vehicle_id']).first():
                    return None, "This vehicle is already listed in another auction."

            if data.get('auction_type') == 'battery':
                if not data.get('battery_id'):
                    return None, "Auction type 'battery' requires a battery_id."
                if Auction.query.filter_by(battery_id=data['battery_id']).first():
                    return None, "This battery is already listed in another auction."
 
            start_time = data['start_time']
            if isinstance(start_time, str):
                start_time = parser.isoparse(start_time)
            start_time_utc = to_utc(start_time)
            current_time = datetime.now(timezone.utc) 
            if start_time_utc <= current_time + timedelta(hours=8):
                return None, "Start time must be at least 8 hours after the current time."

            end_time = start_time_utc + timedelta(hours=2)

            new_auction = Auction(
                bidder_id=data['bidder_id'],
                battery_id=data.get('battery_id'),
                vehicle_id=data.get('vehicle_id'),
                auction_type=data['auction_type'],
                start_time=start_time_utc,
                end_time=end_time,
                current_bid=data['current_bid'],
                auction_status='pending'
            )

            db.session.add(new_auction)
            db.session.commit()
            db.session.refresh(new_auction)
            return new_auction, "Auction created successfully."

        except Exception as e:
            db.session.rollback()
            print(f"Lỗi khi thêm đấu giá: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return None, f"An internal error occurred: {str(e)}"


    @staticmethod
    def update_auction_metadata(auction_id, user_id, data): 
        try:
            auction = db.session.get(Auction, auction_id)
            if not auction:
                return None, "Auction not found."

            if auction.bidder_id != user_id:
                return None, "You do not have permission to edit this auction."

            current_time = datetime.now(timezone.utc)
            start_time_utc = to_utc(auction.start_time)
 
            if current_time >= (start_time_utc - timedelta(hours=8)):
                return None, "You can only edit an auction at least 8 hour before it starts."
 
            if 'start_time' in data:
                new_start = data['start_time']
                if isinstance(new_start, str):
                    new_start = parser.isoparse(new_start)
                new_start_utc = to_utc(new_start)
                if new_start_utc <= current_time + timedelta(hours=8):
                    return None, "New start time must be at least 8 hour after the current time."

                auction.start_time = new_start_utc
                auction.end_time = new_start_utc + timedelta(hours=2)

            if 'current_bid' in data:
                auction.current_bid = float(data['current_bid'])

            db.session.commit()
            db.session.refresh(auction)
            return auction, "Auction updated successfully."

        except Exception as e:
            db.session.rollback()
            print(f"Lỗi khi cập nhật đấu giá: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return None, f"An internal error occurred: {str(e)}"


    @staticmethod
    def delete_auction(auction_id, user_id, user_role): 
        try:
            auction = db.session.get(Auction, auction_id)
            if not auction:
                return False, "Auction not found."

            if auction.bidder_id != user_id and user_role != 'admin':
                return False, "You do not have permission to delete this auction."
            if user_role == 'admin':
                db.session.delete(auction)
                db.session.commit()
                return True, "Auction deleted successfully."
            current_time = datetime.now(timezone.utc)
            start_time_utc = to_utc(auction.start_time)
 
            if start_time_utc - current_time <= timedelta(hours=8):
                return False, "You can only delete an auction at least 8 hour before it starts."
 
            if auction.winning_bidder_id:
                return False, "You can not delete beacause have a winner."

            db.session.delete(auction)
            db.session.commit()
            return True, "Auction deleted successfully."

        except Exception as e:
            db.session.rollback()
            print(f"Lỗi khi xóa đấu giá: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return False, f"An error occurred: {str(e)}"
        
    @staticmethod
    def delete_vehicle_auction(vehicle_id, user_id): 
        try:
            auction = Auction.query.filter_by(vehicle_id=vehicle_id).first()
            if not auction:
                return False, "Auction not found.", 404

            if auction.bidder_id != user_id:
                return False, "You do not have permission to delete this auction.", 403
            current_time = datetime.now(timezone.utc)
            start_time_utc = to_utc(auction.start_time) 
            if start_time_utc - current_time <= timedelta(hours=8) and start_time_utc > current_time:
                return False, "You can only delete an auction at least 8 hour before it starts." , 400
            if auction.winning_bidder_id:
                return False, "You can not delete beacause have a winner." , 400
            db.session.delete(auction)
            db.session.commit()
            return True, "Auction deleted successfully.", 200

        except Exception as e:
            db.session.rollback()
            print(f"Lỗi khi xóa đấu giá: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return False, f"An error occurred: {str(e)}"        
    @staticmethod
    def delete_battery_auction(battery_id, user_id): 
        try:
            auction = Auction.query.filter_by(battery_id=battery_id).first()
            if not auction:
                return False, "Auction not found.",404

            if auction.bidder_id != user_id:
                return False, "You do not have permission to delete this auction.",403
            current_time = datetime.now(timezone.utc)
            start_time_utc = to_utc(auction.start_time) 
            if start_time_utc - current_time <= timedelta(hours=8) and start_time_utc > current_time:
                return False, "You can only delete an auction at least 8 hour before it starts." ,400
            if auction.winning_bidder_id:
                return False, "You can not delete beacause have a winner." , 400
            db.session.delete(auction)
            db.session.commit()
            return True, "Auction deleted successfully.", 200

        except Exception as e:
            db.session.rollback()
            print(f"Lỗi khi xóa đấu giá: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return False, f"An error occurred: {str(e)}"

    @staticmethod
    def place_bid(auction_id, bidder_id, bid_amount):
        try:
            auction = db.session.get(Auction, auction_id)
            if not auction:
                return None, "Auction not found."

            current_time = datetime.now(timezone.utc)
            end_time_utc = to_utc(auction.end_time)
            start_time_utc = to_utc(auction.start_time)

            if start_time_utc > current_time:
                return None, "The auction has not started yet."
            if end_time_utc < current_time:
                auction.auction_status = 'ended'
                db.session.commit()
                return None, "The auction has already ended."
            if bid_amount <= auction.current_bid:
                return None, f"Your bid must be greater than the current bid of {auction.current_bid}."
            if bidder_id == auction.bidder_id:
                return None, "You cannot bid on your own auction."

            auction.current_bid = bid_amount
            auction.winning_bidder_id = bidder_id
            auction.auction_status = 'started'

            db.session.commit()
            db.session.refresh(auction)
            return auction, f"Bid placed successfully. New current bid: {bid_amount}."

        except Exception as e:
            db.session.rollback()
            print(f"Lỗi khi đặt giá: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return None, f"An internal error occurred: {str(e)}"


    @staticmethod
    def get_all_active_auctions(): 
        current_time = datetime.now(timezone.utc) 
        active_statuses = ['prepare', 'started']
        
        return Auction.query.filter(
            Auction.auction_status.in_(active_statuses),
            Auction.end_time > current_time  
        ).order_by(Auction.start_time.asc()).all()

    @staticmethod
    def get_auction_by_id(auction_id):
        return db.session.get(Auction, auction_id)
    
    @staticmethod
    def get_auction_by_vehicle_id(vehicle_id):
        return Auction.query.filter_by(vehicle_id=vehicle_id).first()
    
    @staticmethod
    def get_auction_by_battery_id(battery_id):
        return Auction.query.filter_by(battery_id=battery_id).first()

    @staticmethod
    def get_auctions_by_creator(bidder_id):
        return Auction.query.filter_by(bidder_id=bidder_id).order_by(Auction.start_time.desc()).all()

    @staticmethod
    def get_auctions_by_winning_bidder(winning_bidder_id):
        return Auction.query.filter_by(winning_bidder_id=winning_bidder_id).order_by(Auction.end_time.desc()).all()
 
    @staticmethod
    def get_auctions_by_status(auction_status): 
        return Auction.query.filter_by(
            auction_status=auction_status
        ).order_by(Auction.start_time.asc()).all()

    @staticmethod
    def manually_finalize_auction(auction_id):
        try:
            auction = db.session.get(Auction, auction_id)
            if not auction:
                return None, "Auction not found."

            if not auction.winning_bidder_id:
                return None, "No winning bid found."

            if to_utc(auction.end_time) > datetime.now(timezone.utc):
                auction.end_time = datetime.now(timezone.utc)

            auction.auction_status = 'ended'

            db.session.commit()
            db.session.refresh(auction)

            winner_name = str(auction.winning_bidder_id) if auction.winning_bidder_id else "Unknown"
            return auction, f"Auction finalized. Winner: {winner_name}"

        except Exception as e:
            db.session.rollback()
            print(f"Lỗi khi hoàn tất đấu giá: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return None, f"An internal error occurred: {str(e)}"
    @staticmethod
    def auto_finalize_auctions(): 
        try:
            current_time = datetime.now(timezone.utc) 
            auctions_to_end = Auction.query.filter(
                Auction.auction_status.in_(['started', 'prepare']),
                Auction.end_time <= current_time
            ).all()

            if not auctions_to_end:
                return 0  

            for auction in auctions_to_end:
                auction.auction_status = 'ended'
            
            db.session.commit()
            print(f"Successfully finalized {len(auctions_to_end)} auctions.")
            return len(auctions_to_end)

        except Exception as e:
            db.session.rollback()
            print(f"Lỗi khi tự động hoàn tất đấu giá: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return -1 
    @staticmethod
    def auto_start_auctions(): 
        try:
            current_time = datetime.now(timezone.utc) 
            auctions_to_start = Auction.query.filter(
                Auction.auction_status == 'prepare',
                Auction.start_time <= current_time,
                Auction.end_time > current_time
            ).all()

            if not auctions_to_start:
                return 0  

            for auction in auctions_to_start:
                auction.auction_status = 'started'
            
            db.session.commit()
            print(f"Hệ thống đã tự động bắt đầu {len(auctions_to_start)} phiên đấu giá.")
            return len(auctions_to_start)

        except Exception as e:
            db.session.rollback()
            print(f"Lỗi khi tự động bắt đầu đấu giá: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return -1   
    @staticmethod
    def review_auction(auction_id, is_approved): 
        try:
            auction = db.session.get(Auction, auction_id)
            if not auction:
                return None, "Auction not found."

            if auction.auction_status != 'pending':
                return None, f"Auction is already {auction.auction_status} and cannot be reviewed."

            if is_approved: 
                current_time = datetime.now(timezone.utc)
                start_time_utc = to_utc(auction.start_time) 
                if start_time_utc <= current_time + timedelta(hours=1):
                    return None, "Cannot approve: Start time must be at least 1 hour from now."

                auction.auction_status = 'prepare'
                message = "Auction approved and is ready to start."
            else:
                auction.auction_status = 'rejected'
                message = "Auction rejected."

            db.session.commit()
            db.session.refresh(auction)
            return auction, message

        except Exception as e:
            db.session.rollback()
            print(f"Lỗi khi duyệt đấu giá: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return None, f"An internal error occurred: {str(e)}"
        
    # @staticmethod 
    # def check_if_resource_is_auctioned(resource_type, resource_id):
    #     try: 
    #         if resource_type == 'vehicle':
    #             condition = (Auction.vehicle_id == resource_id)
    #         elif resource_type == 'battery': 
    #             condition = (Auction.battery_id == resource_id)
    #         else:
    #             return {"is_auctioned": False, "auction_status": None}
    
    #         auction = db.session.query(Auction)\
    #             .filter(condition)\
    #             .first()

    #         if not auction: 
    #             return {"is_auctioned": False, "auction_status": None} 
    #         active_statuses = ['pending', 'prepare','started']
    #         #  nonactive_statuses = ['ended', 'rejected']
            
    #         return {
    #             "is_auctioned": auction.auction_status in active_statuses,
    #             "auction_status": auction.auction_status
    #         } 
    #     except Exception as e:
    #         logger.error(f"Error checking auction status for {resource_type} ID {resource_id}: {e}")
    #         return {"is_auctioned": False, "auction_status": None}

    @staticmethod
    def check_if_resource_is_auctioned(resource_type, resource_id) :
        try: 
            filter_condition = None
            if resource_type == 'vehicle':
                filter_condition = (Auction.vehicle_id == resource_id)
            elif resource_type == 'battery':
                filter_condition = (Auction.battery_id == resource_id)
            else:
                return False 
            active_statuses = ['pending', 'prepare', 'started', 'ended', 'rejected'] 
            auction = db.session.query(Auction).filter(
                and_(
                    filter_condition, 
                    Auction.auction_status.in_(active_statuses)
                )
            ).first()
            return auction is not None
                    
        except Exception as e:
            logger.error(f"Error checking auction status for {resource_type} ID {resource_id}: {e}")
            return False
        
    @staticmethod
    def check_status_if_resource_is_auctioned(resource_type, resource_id) :
        try: 
            filter_condition = None
            if resource_type == 'vehicle':
                filter_condition = (Auction.vehicle_id == resource_id)
            elif resource_type == 'battery':
                filter_condition = (Auction.battery_id == resource_id)
            else:
                return None 
            active_statuses = ['pending', 'prepare', 'started', 'ended', 'rejected'] 
            auction = db.session.query(Auction).filter(
                and_(
                    filter_condition, 
                    Auction.auction_status.in_(active_statuses)
                )
            ).first()
            return auction.auction_status
                    
        except Exception as e:
            logger.error(f"Error checking auction status for {resource_type} ID {resource_id}: {e}")
            return None

    @staticmethod
    def get_absolutely_all_auctions(): 
        return Auction.query.order_by(Auction.start_time.desc()).all()
    @staticmethod
    def get_pending_auctions(): 
        return Auction.query.filter_by(auction_status='pending').order_by(Auction.start_time.asc()).all()
    @staticmethod
    def update_auction_status(auction_id, new_status): 
        auction = Auction.query.get(auction_id)
        if not auction: return None, "auction not found."
        
        allowed_statuses = ['pending', 'prepare','started', 'ended', 'rejected']
        if new_status not in allowed_statuses: return None, "Invalid status."
            
        auction.auction_status = new_status
        db.session.commit()
        return auction, "Status updated successfully."
