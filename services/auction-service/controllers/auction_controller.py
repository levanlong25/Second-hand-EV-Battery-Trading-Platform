from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from services.auction_service import AuctionService  
from functools import wraps
from dateutil import parser
import requests  
import logging   
import os

# --- Blueprint và Cấu hình ---
auction_bp = Blueprint('auction_api', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)

LISTING_SERVICE_URL = os.environ.get('LISTING_SERVICE_URL', 'http://listing-service:5001')
USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL', 'http://user-service:5000')
REQUEST_TIMEOUT = 3


def get_user_info_by_id(user_id: int): 
    if not user_id:
        return None 
    url = f"{USER_SERVICE_URL}/api/info/{user_id}"  
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200: 
            user_data_list = response.json()
            if user_data_list and isinstance(user_data_list, list) and len(user_data_list) > 0:
                 return user_data_list[0] 
            else:
                 logger.warning(f"User Service returned empty or invalid data for user ID {user_id} at {url}")
                 return None
        elif response.status_code == 404:
             logger.warning(f"User not found in User Service for ID {user_id} at {url}")
             return None  
        else: 
            logger.warning(f"User Service returned status {response.status_code} for user ID {user_id} at {url}")
            return None
    except requests.exceptions.RequestException as e: 
        logger.error(f"Failed to connect to User Service at {url} for user info: {e}")
        return None
    
# --- Custom Decorator for Admin Role ---
def admin_required():
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            claims = get_jwt()
            if claims.get("role") != "admin":
                return jsonify({"error": "Admin access required"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper


 
def serialize_auction(auction): 
    if not auction: 
        return None
    return {
        'auction_id': auction.auction_id,
        'auction_type': auction.auction_type,
        'vehicle_id': auction.vehicle_id,   
        'battery_id': auction.battery_id,  
        'auction_status': auction.auction_status,
        'start_time': auction.start_time.isoformat(),
        'end_time': auction.end_time.isoformat(),
        'current_bid': str(auction.current_bid),
        'bidder_id': auction.bidder_id,  
        'winning_bidder_id': auction.winning_bidder_id  
    }
 
def _package_auction_details(auction): 
    if not auction:
        return jsonify({"error": "Auction not found"}), 404
        
    auction_data = serialize_auction(auction)  
    if auction_data.get('auction_type') == 'vehicle' and auction_data.get('vehicle_id'):
        auction_data['vehicle_details'] = get_and_serialize_vehicle_by_id(auction_data['vehicle_id'])
    elif auction_data.get('auction_type') == 'battery' and auction_data.get('battery_id'):
        auction_data['battery_details'] = get_and_serialize_battery_by_id(auction_data['battery_id'])
        
    seller_info = None
    if auction_data.get('bidder_id'):
        seller_info = get_user_info_by_id(auction_data['bidder_id'])
    if seller_info and 'username' in seller_info:
        auction_data['seller_username'] = seller_info['username']

    winner_info = None
    winning_bidder_id = auction_data.get('winning_bidder_id')  
    if winning_bidder_id:  
        winner_info = get_user_info_by_id(winning_bidder_id)
    if winner_info and 'username' in winner_info:
        auction_data['winner_username'] = winner_info['username']
    return jsonify(auction_data), 200

@auction_bp.route('/check/<resource_type>/<int:resource_id>', methods=['GET'])
def check_auction_status(resource_type, resource_id): 
    if resource_type not in ['vehicle', 'battery']:
        return jsonify({"error": "Invalid resource type"}), 400 
    is_auctioned_status = AuctionService.check_if_resource_is_auctioned(resource_type, resource_id) 
    return jsonify({"is_auctioned": is_auctioned_status}), 200

# ============================================
# === AUCTION API - ADMIN ENDPOINTS ===
# ============================================

@auction_bp.route('/admin/<int:auction_id>/finalize', methods=['PUT'])
@admin_required()
def finalize_auction(auction_id): 
    auction, message = AuctionService.manually_finalize_auction(auction_id)
    if not auction:
        return jsonify({"error": message}), 400
    
    return jsonify({"message": message, "auction": serialize_auction(auction)}), 200 

@auction_bp.route('/admin/pending', methods=['GET'])
@admin_required()
def get_pending_auctions(): 
    auctions = AuctionService.get_auctions_by_status('pending')
    return jsonify([serialize_auction(a) for a in auctions]), 200

@auction_bp.route('/admin/review', methods=['POST'])
@admin_required()
def review_auction():  
    data = request.get_json()
    if not data or 'auction_id' not in data or data.get('approve') is None:
        return jsonify({"error": "Missing 'auction_id' or 'approve' (true/false) in request body"}), 400
    
    auction_id = data.get('auction_id')
    is_approved = bool(data.get('approve'))

    auction, message = AuctionService.review_auction(auction_id, is_approved)
    
    if not auction:
        return jsonify({"error": message}), 400
    
    return jsonify({"message": message, "auction": serialize_auction(auction)}), 200


@auction_bp.route('/admin/all-auctions', methods=['GET'])
@admin_required()
def get_all_auctions_for_admin():
    """Lấy TOÀN BỘ tin đăng cho trang admin."""
    auctions = AuctionService.get_absolutely_all_auctions()
    return jsonify([serialize_auction(l) for l in auctions]), 200

@auction_bp.route('/admin/auctions/pending', methods=['GET'])
@admin_required()
def get_pending_auctions_admin():
    auctions = AuctionService.get_pending_auctions()
    return jsonify([serialize_auction(l) for l in auctions]), 200

@auction_bp.route('/admin/auctions/<int:auction_id>/auction_status', methods=['PUT'])
@admin_required()
def update_auction_status_admin(auction_id):
    data = request.get_json()
    new_status = data.get('auction_status')
    if not new_status: return jsonify({"error": "Missing 'status' in request body"}), 400
        
    auction, message = AuctionService.update_auction_status(auction_id, new_status)
    if not auction: return jsonify({"error": message}), 404
        
    return jsonify({"message": message, "auction": serialize_auction(auction)}), 200
