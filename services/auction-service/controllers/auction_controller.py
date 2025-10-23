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
REQUEST_TIMEOUT = 1


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

def get_and_serialize_vehicle_by_id(vehicle_id: int): 
    if not vehicle_id: return None 
    url = f"{LISTING_SERVICE_URL}/api/vehicles/{vehicle_id}" 
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200: 
            return response.json() 
        else: 
            logger.warning(f"Listing Service returned status {response.status_code} for vehicle ID {vehicle_id} at {url}")
            return None
    except requests.exceptions.RequestException as e: 
         logger.error(f"Failed to connect to Listing Service at {url} for vehicle details: {e}")
         return None

def get_and_serialize_battery_by_id(battery_id: int): 
     if not battery_id: return None
     url = f"{LISTING_SERVICE_URL}/api/batteries/{battery_id}"
     try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200: 
             return response.json()
        else: 
             logger.warning(f"Listing Service returned status {response.status_code} for battery ID {battery_id} at {url}")
             return None
     except requests.exceptions.RequestException as e: 
          logger.error(f"Failed to connect to Listing Service at {url} for battery details: {e}")
          return None
 
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

@auction_bp.route('/check-status/<resource_type>/<int:resource_id>', methods=['GET'])
def check_status_auction_status(resource_type, resource_id): 
    if resource_type not in ['vehicle', 'battery']:
        return jsonify({"error": "Invalid resource type"}), 400 
    is_auctioned_status = AuctionService.check_status_if_resource_is_auctioned(resource_type, resource_id) 
    return jsonify({"auction_status_resource": is_auctioned_status}), 200

# ============================================
# === AUCTION API - PUBLIC ENDPOINTS ===
# ============================================

@auction_bp.route('/', methods=['GET'])
def get_active_auctions(): 
    auctions = AuctionService.get_all_active_auctions()
    enriched_auctions = []
    for auction in auctions:
        auction_data = serialize_auction(auction) 
        if auction_data.get('auction_type') == 'vehicle' and auction_data.get('vehicle_id'):
            auction_data['vehicle_details'] = get_and_serialize_vehicle_by_id(auction_data['vehicle_id'])
        elif auction_data.get('auction_type') == 'battery' and auction_data.get('battery_id'):
            auction_data['battery_details'] = get_and_serialize_battery_by_id(auction_data['battery_id'])
         
        seller_info = get_user_info_by_id(auction_data.get('bidder_id'))
        if seller_info and 'username' in seller_info:
             auction_data['seller_username'] = seller_info['username']

        winner_info = None
        winning_bidder_id = auction_data.get('winning_bidder_id')
        if winning_bidder_id:
            winner_info = get_user_info_by_id(winning_bidder_id)
        if winner_info and 'username' in winner_info:
            auction_data['winner_username'] = winner_info['username']
        enriched_auctions.append(auction_data)
        
    return jsonify(enriched_auctions), 200

@auction_bp.route('/<int:auction_id>', methods=['GET'])
def get_auction_details(auction_id): 
    auction = AuctionService.get_auction_by_id(auction_id)
    if not auction:
        return jsonify({"error": "Auction not found"}), 404
    return _package_auction_details(auction)

@auction_bp.route('/vehicle/<int:vehicle_id>', methods=['GET'])
def get_auction_vehicle_details(vehicle_id): 
    auction = AuctionService.get_auction_by_vehicle_id(vehicle_id)
    if not auction:
        return jsonify({"error": "Auction not found"}), 404
    return _package_auction_details(auction)

@auction_bp.route('/battery/<int:battery_id>', methods=['GET'])
def get_auction_battery_details(battery_id): 
    auction = AuctionService.get_auction_by_battery_id(battery_id)
    if not auction:
        return jsonify({"error": "Auction not found"}), 404
    return _package_auction_details(auction)
# ============================================
# === AUCTION API - PROTECTED ENDPOINTS ===
# ============================================

@auction_bp.route('/', methods=['POST'])
@jwt_required()
def create_auction(): 
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
 
    data['bidder_id'] = current_user_id
     
    if 'start_time' in data and isinstance(data['start_time'], str):
        try:
            data['start_time'] = parser.isoparse(data['start_time'])
        except ValueError:
            return jsonify({"error": "Invalid start_time format. Use ISO 8601 format."}), 400

    auction, message = AuctionService.add_auction(data)
    if not auction:
        return jsonify({"error": message}), 400
    
    return jsonify({"message": message, "auction": serialize_auction(auction)}), 201

@auction_bp.route('/<int:auction_id>', methods=['PUT'])
@jwt_required()
def update_auction(auction_id): 
    current_user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
 
    if 'start_time' in data and isinstance(data['start_time'], str):
        try:
            data['start_time'] = parser.isoparse(data['start_time'])
        except ValueError:
            return jsonify({"error": "Invalid start_time format. Use ISO 8601 format."}), 400

    auction, message = AuctionService.update_auction_metadata(auction_id, current_user_id, data)
    if not auction:
        return jsonify({"error": message}), 403  
        
    return jsonify({"message": message, "auction": serialize_auction(auction)}), 200

@auction_bp.route('/auctions/<int:auction_id>', methods=['DELETE'])
@jwt_required()
def delete_auction(auction_id): 
    current_user_id = int(get_jwt_identity())
    user_role = get_jwt().get("role")

    success, message = AuctionService.delete_auction(auction_id, current_user_id, user_role)
    if not success:
        return jsonify({"error": message}), 403
    
    return jsonify({"message": message}), 200

@auction_bp.route('/auctions/vehicles/<int:vehicle_id>', methods=['DELETE'])
@jwt_required()
def delete_vehicle_auction(vehicle_id): 
    current_user_id = int(get_jwt_identity())

    success, message, status_code = AuctionService.delete_vehicle_auction(vehicle_id, current_user_id)
    if not success:
        return jsonify({"error": message}), status_code
    
    return jsonify({"message": message}), 200

@auction_bp.route('/auctions/batteries/<int:battery_id>', methods=['DELETE'])
@jwt_required()
def delete_battery_auction(battery_id): 
    current_user_id = int(get_jwt_identity())

    success, message, status_code = AuctionService.delete_battery_auction(battery_id, current_user_id)
    if not success:
        return jsonify({"error": message}), status_code
    
    return jsonify({"message": message}), 200

@auction_bp.route('/<int:auction_id>/bid', methods=['POST'])
@jwt_required()
def place_bid(auction_id): 
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or 'bid_amount' not in data:
        return jsonify({"error": "Missing 'bid_amount' in request body"}), 400
    
    try:
        bid_amount = float(data['bid_amount'])
    except (ValueError, TypeError):
        return jsonify({"error": "'bid_amount' must be a valid number"}), 400

    auction, message = AuctionService.place_bid(auction_id, current_user_id, bid_amount)
    if not auction:
        return jsonify({"error": message}), 400
        
    return jsonify({"message": message, "auction": serialize_auction(auction)}), 200

# ============================================
# === AUCTION API - "MY" ENDPOINTS ===
# ============================================

@auction_bp.route('/my-auctions', methods=['GET'])
@jwt_required()
def get_my_created_auctions(): 
    current_user_id = int(get_jwt_identity())
    auctions = AuctionService.get_auctions_by_creator(current_user_id)
    return jsonify([serialize_auction(a) for a in auctions]), 200

@auction_bp.route('/my-bids', methods=['GET'])
@jwt_required()
def get_my_winning_bids(): 
    current_user_id = int(get_jwt_identity())
    auctions = AuctionService.get_auctions_by_winning_bidder(current_user_id)
    return jsonify([serialize_auction(a) for a in auctions]), 200

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
