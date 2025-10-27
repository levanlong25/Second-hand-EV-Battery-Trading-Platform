from datetime import datetime, timezone, timedelta
from dateutil import parser
import sys, traceback
from sqlalchemy import or_, and_
from app import db
from models.auction import Auction
import logging
import pytz
import os
import requests
from flask import current_app

VIETNAM_TZ = pytz.timezone('Asia/Ho_Chi_Minh')
ALLOWED_START_HOURS = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]
TRANSACTION_SERVICE_URL = os.environ.get('TRANSACTION_SERVICE_URL', 'http://transaction-service:5003')
REQUEST_TIMEOUT = 1

logger = logging.getLogger(__name__)

def to_utc(dt): 
    if dt is None:
        return None
    if dt.tzinfo is None: 
        return dt.replace(tzinfo=timezone.utc) 
    return dt.astimezone(timezone.utc)

def is_valid_start_time_slot(dt_utc: datetime): 
    if not dt_utc:
        return False
    try:
        local_dt = dt_utc.astimezone(VIETNAM_TZ)
        return (local_dt.hour in ALLOWED_START_HOURS and
                local_dt.minute == 0 and
                local_dt.second == 0 and
                local_dt.microsecond == 0)
    except Exception:
        return False 

class AuctionService:
    @staticmethod
    def add_auction(data):
        required_fields = ['bidder_id', 'auction_type', 'start_time', 'current_bid']
        if not all(field in data for field in required_fields):
            return None, "Thiếu các trường bắt buộc."

        try:
            auction_type = data.get('auction_type')
            vehicle_id = data.get('vehicle_id')
            battery_id = data.get('battery_id') 
            if auction_type == 'vehicle':
                if not vehicle_id:
                    return None, "Loại đấu giá 'vehicle' yêu cầu vehicle_id."
                if Auction.query.filter_by(vehicle_id=vehicle_id, auction_status='pending').first() or \
                   Auction.query.filter_by(vehicle_id=vehicle_id, auction_status='prepare').first() or \
                   Auction.query.filter_by(vehicle_id=vehicle_id, auction_status='started').first():
                    return None, "Xe này đã có trong một phiên đấu giá khác."
            elif auction_type == 'battery':
                if not battery_id:
                    return None, "Loại đấu giá 'battery' yêu cầu battery_id."
                if Auction.query.filter_by(battery_id=battery_id, auction_status='pending').first() or \
                   Auction.query.filter_by(battery_id=battery_id, auction_status='prepare').first() or \
                   Auction.query.filter_by(battery_id=battery_id, auction_status='started').first():
                   return None, "Pin này đã có trong một phiên đấu giá khác."
            else:
                 return None, "Loại đấu giá không hợp lệ." 
            start_time_input = data['start_time']
            if isinstance(start_time_input, str):
                try: 
                    start_time = parser.isoparse(start_time_input)
                    if start_time.tzinfo is None: 
                        start_time = VIETNAM_TZ.localize(start_time)
                except ValueError:
                    return None, "Định dạng start_time không hợp lệ. Sử dụng ISO 8601."
            elif isinstance(start_time_input, datetime):
                 start_time = start_time_input  
            else:
                 return None, "start_time phải là chuỗi ISO 8601 hoặc datetime object."

            start_time_utc = to_utc(start_time)
            current_time_utc = datetime.now(timezone.utc) 
            if start_time_utc <= current_time_utc:
                return None, "Vui lòng chọn thời gian hợp lệ sau thời điểm hiện tại." 
            if not is_valid_start_time_slot(start_time_utc):
                return None, f"Thời gian bắt đầu phải là một trong các mốc giờ: {', '.join(map(str, ALLOWED_START_HOURS))}:00 (giờ Việt Nam)." 
            end_time_utc = start_time_utc + timedelta(hours=2) 
            new_auction = Auction(
                bidder_id=data['bidder_id'],
                battery_id=battery_id,
                vehicle_id=vehicle_id,
                auction_type=auction_type,
                start_time=start_time_utc,
                end_time=end_time_utc,
                current_bid=float(data['current_bid']), # Ensure starting bid is float
                auction_status='pending' # Initial status
            )

            db.session.add(new_auction)
            db.session.commit()
            db.session.refresh(new_auction)
            return new_auction, "Tạo phiên đấu giá thành công, đang chờ duyệt."

        except Exception as e:
            db.session.rollback()
            logger.error(f"Lỗi khi thêm đấu giá: {e}", exc_info=True)
            return None, f"Lỗi máy chủ nội bộ: {str(e)}"

    @staticmethod
    def update_auction_metadata(auction_id, user_id, data):
        try:
            auction = db.session.get(Auction, auction_id)
            if not auction:
                return None, "Không tìm thấy phiên đấu giá."

            if auction.bidder_id != user_id:
                return None, "Bạn không có quyền chỉnh sửa phiên đấu giá này." 
            current_time_utc = datetime.now(timezone.utc)
            start_time_utc = to_utc(auction.start_time)  
            if current_time_utc >= start_time_utc:
                return None, "Không thể chỉnh sửa phiên đấu giá đã bắt đầu hoặc đã kết thúc." 
            updated = False
            if 'start_time' in data:
                new_start_input = data['start_time']
                if isinstance(new_start_input, str):
                    try:
                        new_start = parser.isoparse(new_start_input)
                    except ValueError:
                         return None, "Định dạng start_time mới không hợp lệ."
                elif isinstance(new_start_input, datetime):
                     new_start = new_start_input
                else:
                     return None, "start_time mới không hợp lệ."

                new_start_utc = to_utc(new_start)

                # 1. Must be in the future
                if new_start_utc <= current_time_utc:
                    return None, "Vui lòng chọn thời gian hợp lệ sau thời điểm hiện tại."

                # 2. Must be an allowed time slot
                if not is_valid_start_time_slot(new_start_utc):
                    return None, f"Thời gian bắt đầu mới phải là một trong các mốc giờ: {', '.join(map(str, ALLOWED_START_HOURS))}:00 (giờ Việt Nam)."

                # Update start and end times
                auction.start_time = new_start_utc
                auction.end_time = new_start_utc + timedelta(hours=2)
                updated = True

            if 'current_bid' in data:
                 try:
                     new_bid = float(data['current_bid'])
                     if new_bid <= 0:
                         return None, "Giá khởi điểm phải lớn hơn 0."
                     auction.current_bid = new_bid
                     updated = True
                 except (ValueError, TypeError):
                     return None, "Giá khởi điểm phải là một số hợp lệ."

            if not updated:
                return auction, "Không có thông tin nào được cập nhật." # Return current auction if no changes

            db.session.commit()
            db.session.refresh(auction)
            return auction, "Cập nhật phiên đấu giá thành công."

        except Exception as e:
            db.session.rollback()
            logger.error(f"Lỗi khi cập nhật đấu giá {auction_id}: {e}", exc_info=True)
            return None, f"Lỗi máy chủ nội bộ: {str(e)}"

    @staticmethod
    def _can_user_delete_auction(auction, user_id, user_role='user'):
        """Helper to check deletion rules."""
        if not auction:
            return False, "Không tìm thấy phiên đấu giá."
 
        if user_role == 'admin':
            return True, "Admin override."
 
        if auction.bidder_id != user_id:
            return False, "Bạn không có quyền xóa phiên đấu giá này."

        current_time_utc = datetime.now(timezone.utc)
        start_time_utc = to_utc(auction.start_time)
        end_time_utc = to_utc(auction.end_time)

        # Case 1: Before start
        if current_time_utc < start_time_utc:
            return True, "Allowed: Before start time."

        # Case 2: After end, no winner
        if current_time_utc > end_time_utc and auction.winning_bidder_id is None:
            return True, "Allowed: After end time with no winner."

        # Case 3: During auction
        if start_time_utc <= current_time_utc <= end_time_utc:
            return False, "Không thể xóa phiên đấu giá đang diễn ra."

        # Case 4: After end with winner
        if current_time_utc > end_time_utc and auction.winning_bidder_id is not None:
             return False, "Không thể xóa phiên đấu giá đã có người thắng."

        # Fallback (shouldn't happen with above logic)
        return False, "Không thể xóa phiên đấu giá ở trạng thái hiện tại."


    @staticmethod
    def delete_auction(auction_id, user_id, user_role):
        try:
            auction = db.session.get(Auction, auction_id)
            
            can_delete, message = AuctionService._can_user_delete_auction(auction, user_id, user_role)

            if not can_delete:
                return False, message

            # If checks pass, delete
            db.session.delete(auction)
            db.session.commit()
            return True, "Xóa phiên đấu giá thành công."

        except Exception as e:
            db.session.rollback()
            logger.error(f"Lỗi khi xóa đấu giá {auction_id}: {e}", exc_info=True)
            return False, f"Lỗi máy chủ nội bộ: {str(e)}"

    @staticmethod
    def delete_vehicle_auction(vehicle_id, user_id):
        try:
            # Find the auction by vehicle_id
            auction = Auction.query.filter_by(vehicle_id=vehicle_id).first()
            if not auction:
                 # Return consistent tuple format (success, message, status_code)
                 return False, "Không tìm thấy phiên đấu giá cho xe này.", 404

            # Use the helper to check deletion rules (pass 'user' role as default)
            can_delete, message = AuctionService._can_user_delete_auction(auction, user_id, 'user')

            if not can_delete:
                # Determine appropriate status code based on message
                status_code = 403 if "quyền" in message else 400
                return False, message, status_code

            # If checks pass, delete
            db.session.delete(auction)
            db.session.commit()
            return True, "Xóa phiên đấu giá thành công.", 200

        except Exception as e:
            db.session.rollback()
            logger.error(f"Lỗi khi xóa đấu giá xe {vehicle_id}: {e}", exc_info=True)
            # Return consistent tuple format
            return False, f"Lỗi máy chủ nội bộ: {str(e)}", 500

    @staticmethod
    def delete_battery_auction(battery_id, user_id):
        try:
            # Find the auction by battery_id
            auction = Auction.query.filter_by(battery_id=battery_id).first()
            if not auction:
                 return False, "Không tìm thấy phiên đấu giá cho pin này.", 404

            # Use the helper to check deletion rules
            can_delete, message = AuctionService._can_user_delete_auction(auction, user_id, 'user')

            if not can_delete:
                status_code = 403 if "quyền" in message else 400
                return False, message, status_code

            # If checks pass, delete
            db.session.delete(auction)
            db.session.commit()
            return True, "Xóa phiên đấu giá thành công.", 200

        except Exception as e:
            db.session.rollback()
            logger.error(f"Lỗi khi xóa đấu giá pin {battery_id}: {e}", exc_info=True)
            return False, f"Lỗi máy chủ nội bộ: {str(e)}", 500

    @staticmethod
    def place_bid(auction_id, bidder_id, bid_amount):
        try:
            auction = db.session.get(Auction, auction_id)
            if not auction:
                return None, "Không tìm thấy phiên đấu giá." 
            if auction.auction_status != 'started':
                return None, f"Phiên đấu giá hiện không ở trạng thái 'started' (trạng thái: {auction.auction_status})." 

            current_time_utc = datetime.now(timezone.utc)
            end_time_utc = to_utc(auction.end_time) 
            start_time_utc = to_utc(auction.start_time) 
            if end_time_utc <= current_time_utc: 
                return None, "Phiên đấu giá đã kết thúc."
            if start_time_utc > current_time_utc: 
                return None, "Phiên đấu giá chưa bắt đầu."
            if bid_amount <= auction.current_bid:
                return None, f"Giá đặt phải lớn hơn giá hiện tại ({auction.current_bid})."
            if bidder_id == auction.bidder_id:  
                return None, "Bạn không thể đặt giá cho phiên đấu giá của chính mình."
            if bidder_id == auction.winning_bidder_id:  
                return None, "Bạn đang là người đấu giá cao nhất."
 
            auction.current_bid = bid_amount
            auction.winning_bidder_id = bidder_id 

            db.session.commit()
            db.session.refresh(auction)
            return auction, f"Đặt giá thành công. Giá hiện tại mới: {bid_amount}."

        except Exception as e:
            db.session.rollback()
            logger.error(f"Lỗi khi đặt giá cho đấu giá {auction_id}: {e}", exc_info=True)
            return None, f"Lỗi máy chủ nội bộ: {str(e)}"

    @staticmethod
    def filter_auctions(filters: dict): 
        query = Auction.query.filter(Auction.auction_status.in_(['prepare', 'started'])) 
        if filters.get("auction_type"):
            query = query.filter(Auction.auction_type == filters["auction_type"]) 
        query = query.order_by(Auction.end_time.asc()) 
        return query.all()

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

            count = 0
            for auction in auctions_to_start:
                auction.auction_status = 'started'
                count += 1
            
            db.session.commit()
            logger.info(f"Hệ thống đã tự động bắt đầu {count} phiên đấu giá.")
            return count

        except Exception as e:
            db.session.rollback()
            logger.error(f"Lỗi khi tự động bắt đầu đấu giá: {e}", exc_info=True)
            return -1

    @staticmethod
    def auto_finalize_auctions():
        try:
            current_time = datetime.now(timezone.utc) 
            auctions_to_end = Auction.query.filter(
                Auction.auction_status == 'started',
                Auction.end_time <= current_time
            ).all()

            if not auctions_to_end:
                return 0  

            ended_count = 0
            transaction_created_count = 0
            transaction_failed_ids = []

            for auction in auctions_to_end: 
                auction.auction_status = 'ended'
                ended_count += 1
 
                if auction.winning_bidder_id is not None:
                    try: 
                        payload = {
                            "auction_id": auction.auction_id, 
                            "listing_id": None,  
                            "seller_id": auction.bidder_id, 
                            "buyer_id": auction.winning_bidder_id,  
                            "final_price": float(auction.current_bid) 
                        } 
                        internal_token = os.environ.get('INTERNAL_SERVICE_TOKEN')
                        api_key = os.environ.get('INTERNAL_API_KEY') 

                        headers = {}
                        if internal_token: 
                            headers['Authorization'] = internal_token 
                        elif api_key:
                             headers['X-Api-Key'] = api_key

                        if not headers:
                             logger.warning(f"Auction {auction.auction_id}: Không tìm thấy INTERNAL_SERVICE_TOKEN hoặc INTERNAL_API_KEY trong env của worker.")

                        logger.info(f"Attempting to create transaction for ended auction: {auction.auction_id}")
                        url = f"{TRANSACTION_SERVICE_URL.rstrip('/')}/api/transactions"
                        logger.info(f"Posting to Transaction service URL: {url} with headers: {headers} and payload: {payload}")
                        logger.info(f"AUCTION_WORKER: Attempting to POST to URL: {url}")  
                        logger.debug(f"AUCTION_WORKER: Headers being sent: {headers}") 
                        response = requests.post(
                            f"{TRANSACTION_SERVICE_URL}/api/transactions",  
                            json=payload,
                            headers=headers, 
                            timeout=REQUEST_TIMEOUT
                        ) 
                        if response.status_code == 201:  
                            logger.info(f"✅ Successfully auto-created Transaction for auction_id={auction.auction_id}.")
                            transaction_created_count += 1
                        else: 
                            logger.warning(f"⚠️ Failed to auto-create Transaction for auction_id={auction.auction_id}. Status: {response.status_code}, Response: {response.text}")
                            logger.warning(f" Posting to Transaction service URL: {url} with headers: {headers} and payload: {payload}")
                            transaction_failed_ids.append(auction.auction_id) 

                    except requests.exceptions.RequestException as ex_req: 
                        logger.error(f"❌ RequestException when creating Transaction for auction_id={auction.auction_id}: {ex_req}")
                        transaction_failed_ids.append(auction.auction_id)
                    except Exception as ex_other: 
                        logger.error(f"❌ Unexpected error creating Transaction for auction_id={auction.auction_id}: {ex_other}", exc_info=True)
                        transaction_failed_ids.append(auction.auction_id)
 
            db.session.commit()
 
            log_message = f"✅ Auto-ended {ended_count} auctions."
            if transaction_created_count > 0:
                log_message += f" Successfully created {transaction_created_count} transactions."
            if transaction_failed_ids:
                log_message += f" ⚠️ Failed to create transactions for auction IDs: {transaction_failed_ids}."
            logger.info(log_message)

            return ended_count  

        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Lỗi nghiêm trọng trong auto_finalize_auctions: {e}", exc_info=True)
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
    
    
    
    