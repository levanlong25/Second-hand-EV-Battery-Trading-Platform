from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from services.auction_service import AuctionService  
from functools import wraps
from dateutil import parser
import requests  
import logging   
import os
import sys
import traceback
import pytz

VIETNAM_TZ = pytz.timezone("Asia/Ho_Chi_Minh")

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

@auction_bp.route('/filter', methods=['GET'])
def filter_auctions_by_type(): 
    try: 
        filters = {
            "auction_type": request.args.get('type') 
        } 
        auction_type = filters.get("auction_type")
        if auction_type and auction_type not in ['vehicle', 'battery']:
             return jsonify({"error": "Invalid auction_type. Must be 'vehicle' or 'battery'."}), 400 
        auctions = AuctionService.filter_auctions(filters) 
        enriched_auctions = []
        for auction in auctions:
            auction_data = serialize_auction(auction)
            vehicle_details = None
            battery_details = None
             
            current_auction_type = auction_data.get('auction_type')
            
            if current_auction_type == 'vehicle' and auction.vehicle_id:
                vehicle_details = get_and_serialize_vehicle_by_id(auction.vehicle_id)
                if vehicle_details:
                    auction_data['vehicle_details'] = vehicle_details
                else:
                    logger.warning(f"Could not fetch vehicle details for auction {auction.auction_id}")

            elif current_auction_type == 'battery' and auction.battery_id:
                battery_details = get_and_serialize_battery_by_id(auction.battery_id)
                if battery_details:
                    auction_data['battery_details'] = battery_details
                else:
                    logger.warning(f"Could not fetch battery details for auction {auction.auction_id}")

            enriched_auctions.append(auction_data)

        return jsonify(enriched_auctions), 200

    except Exception as e:
        logger.error(f"Error in filter_auctions: {str(e)}", exc_info=True)
        return jsonify({"error": "An internal server error occurred while filtering auctions."}), 500

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
    local_start_time = auction.start_time.astimezone(VIETNAM_TZ) if auction.start_time else None
    local_end_time = auction.end_time.astimezone(VIETNAM_TZ) if auction.end_time else None

    return {
        'auction_id': auction.auction_id,
        'auction_type': auction.auction_type,
        'vehicle_id': auction.vehicle_id,   
        'battery_id': auction.battery_id,  
        'auction_status': auction.auction_status,
        'start_time': local_start_time.isoformat() if local_start_time else None,
        'end_time': local_end_time.isoformat() if local_end_time else None,
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
    try:  
        auction, message = AuctionService.add_auction(data)
        if not auction: 
            return jsonify({"error": message}), 400

        return jsonify({"message": message, "auction": serialize_auction(auction)}), 201
    except Exception as e:  
         logger.error(f"Error creating auction: {e}", exc_info=True)
         return jsonify({"error": "An internal error occurred."}), 500

@auction_bp.route('/<int:auction_id>', methods=['PUT'])
@jwt_required()
def update_auction(auction_id):
    current_user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Service layer handles datetime parsing and validation
    try: # Wrap service call
        auction, message = AuctionService.update_auction_metadata(auction_id, current_user_id, data)
        if not auction:
            # Service layer determines if it's permission error (403) or validation (400) or not found (404)
            status_code = 400 # Default bad request
            if "permission" in message.lower():
                status_code = 403
            elif "not found" in message.lower():
                 status_code = 404
            return jsonify({"error": message}), status_code

        return jsonify({"message": message, "auction": serialize_auction(auction)}), 200
    except Exception as e: # Catch potential unexpected errors
         logger.error(f"Error updating auction {auction_id}: {e}", exc_info=True)
         return jsonify({"error": "An internal error occurred."}), 500

@auction_bp.route('/auctions/<int:auction_id>', methods=['DELETE'])
@jwt_required()
def delete_auction(auction_id):
    current_user_id = int(get_jwt_identity())
    user_role = get_jwt().get("role", "user") # Default to 'user' if role is missing

    try: # Wrap service call
        success, message = AuctionService.delete_auction(auction_id, current_user_id, user_role)
        if not success:
            # Service layer determines the reason and appropriate code (403/404/400)
            status_code = 400 # Default
            if "permission" in message.lower():
                status_code = 403
            elif "not found" in message.lower():
                status_code = 404
            return jsonify({"error": message}), status_code

        return jsonify({"message": message}), 200 # 200 OK on successful deletion
    except Exception as e: # Catch potential unexpected errors
         logger.error(f"Error deleting auction {auction_id}: {e}", exc_info=True)
         return jsonify({"error": "An internal error occurred."}), 500


@auction_bp.route('/auctions/vehicles/<int:vehicle_id>', methods=['DELETE'])
@jwt_required()
def delete_vehicle_auction(vehicle_id):
    current_user_id = int(get_jwt_identity()) 
    try: 
        success, message, status_code = AuctionService.delete_vehicle_auction(vehicle_id, current_user_id)
        if not success:
            return jsonify({"error": message}), status_code

        return jsonify({"message": message}), status_code  
    except Exception as e:  
         logger.error(f"Error deleting vehicle auction {vehicle_id}: {e}", exc_info=True)
         return jsonify({"error": "An internal error occurred."}), 500 

@auction_bp.route('/auctions/batteries/<int:battery_id>', methods=['DELETE'])
@jwt_required()
def delete_battery_auction(battery_id):
    current_user_id = int(get_jwt_identity()) 
    try:  
        success, message, status_code = AuctionService.delete_battery_auction(battery_id, current_user_id)
        if not success:
            return jsonify({"error": message}), status_code

        return jsonify({"message": message}), status_code  
    except Exception as e: 
         logger.error(f"Error deleting battery auction {battery_id}: {e}", exc_info=True)
         return jsonify({"error": "An internal error occurred."}), 500 
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

    try:   
        auction, message = AuctionService.place_bid(auction_id, current_user_id, bid_amount)
        if not auction: 
            return jsonify({"error": message}), 400  

        return jsonify({"message": message, "auction": serialize_auction(auction)}), 200
    except Exception as e:  
         logger.error(f"Error placing bid on auction {auction_id}: {e}", exc_info=True)
         return jsonify({"error": "An internal error occurred."}), 500

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
