from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from services.listing_service import ListingService
from services.vehicle_service import VehicleService
from services.battery_service import BatteryService
from services.comparison_service import ComparisonService
from models.listing_image import ListingImage
from models.listing import Listing
from models.watchlist import WatchList
from werkzeug.utils import secure_filename
from functools import wraps
from app import db
import uuid
import os
import requests
import logging
from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError
  
logger = logging.getLogger(__name__)
api_bp = Blueprint('api', __name__, url_prefix='/api')
AUCTION_SERVICE_URL = os.environ.get('AUCTION_SERVICE_URL', 'http://auction-service:5002')
TRANSACTION_SERVICE_URL = os.environ.get('TRANSACTION_SERVICE_URL', 'http://transaction-service:5003')
REQUEST_TIMEOUT = 1


def service_or_user_required(): 
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs): 
            auth_header = request.headers.get('Authorization')
            internal_token = current_app.config.get('INTERNAL_SERVICE_TOKEN') 
            if auth_header and internal_token and auth_header == internal_token: 
                return fn(*args, **kwargs)
 
            try:
                verify_jwt_in_request() 
            except (NoAuthorizationError, InvalidHeaderError, Exception) as e: 
                return jsonify({"error": f"Unauthorized: Yêu cầu thiếu JWT hợp lệ hoặc Service Token. Lỗi: {str(e)}"}), 401
        return decorator
    return wrapper
def is_auctioned(resource_type, resource_id):  
    if not resource_id or resource_id <= 0:
        return False 
    url = f"{AUCTION_SERVICE_URL}/api/check/{resource_type}/{resource_id}" 
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT) 
        if response.status_code == 200:
            data = response.json() 
            return data.get('is_auctioned', False) 
        elif response.status_code == 404:
            return False 
        logger.warning(
            f"Auction Service returned status {response.status_code} "
            f"for {resource_type} ID {resource_id}: {response.text}"
        )
        return False 
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect or request Auction Service (Resource ID: {resource_id}): {e}")
        return False
    
def auction_status(resource_type, resource_id):  
    if not resource_id or resource_id <= 0:
        return { "auction_status_resource": None}
    url = f"{AUCTION_SERVICE_URL}/api/check-status/{resource_type}/{resource_id}" 
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT) 
        if response.status_code == 200:
            data = response.json() 
            return { "auction_status_resource": data.get("auction_status_resource")}
        elif response.status_code == 404:
            return { "auction_status_resource": None}
        logger.warning(
            f"Auction Service returned status {response.status_code} "
            f"for {resource_type} ID {resource_id}: {response.text}"
        )
        return { "auction_status_resource": None}
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect or request Auction Service (Resource ID: {resource_id}): {e}")
        return { "auction_status_resource": None}

def has_active_transaction(listing_id: int): 
    if not listing_id or listing_id <= 0:
        return False, "Invalid ID"
     
    url = f"{TRANSACTION_SERVICE_URL}/internal/check-listing-transaction/{listing_id}"
     
    internal_api_key = os.environ.get('INTERNAL_API_KEY')
    if not internal_api_key:
        logger.error(f"Kiểm tra giao dịch Listing {listing_id}: INTERNAL_API_KEY không được cấu hình.") 
        return True, "Lỗi cấu hình nội bộ (API Key)."

    headers = {'X-Internal-Api-Key': internal_api_key}
    
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json() 
            return data.get('has_transaction', False), data.get('status', None)
        else: 
            logger.warning(f"Transaction Service trả về lỗi {response.status_code} khi kiểm tra listing {listing_id}: {response.text}") 
            return True, f"Lỗi kiểm tra giao dịch (Code: {response.status_code})."
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Không thể kết nối Transaction Service để kiểm tra listing {listing_id}: {e}") 
        return True, f"Lỗi kết nối dịch vụ giao dịch."
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

def _serialize_vehicle_basic(vehicle): 
    if not vehicle: return None 
    return {
        'vehicle_id': vehicle.vehicle_id,
        'user_id': vehicle.user_id,
        'brand': vehicle.brand,
        'model': vehicle.model,
        'year': vehicle.year,
        'mileage': vehicle.mileage
    }

def _serialize_battery_basic(battery): 
    if not battery: return None 
    return {
        'battery_id': battery.battery_id,
        'user_id': battery.user_id,
        'manufacturer': battery.manufacturer,
        'capacity_kwh': battery.capacity_kwh,
        'health_percent': battery.health_percent
    }

def serialize_vehicle(vehicle):
    if not vehicle: return None 
    is_auctioned_status = None
    auction_status_resource = None
    sale_status = None
    if vehicle.listing :
        sale_status = vehicle.listing.status
    if not vehicle.listing:
        is_auctioned_status = is_auctioned('vehicle', vehicle.vehicle_id)
    if not vehicle.listing:
        auction_status_resource = auction_status('vehicle', vehicle.vehicle_id)
    return {
        'vehicle_id': vehicle.vehicle_id,
        'user_id': vehicle.user_id,
        'brand': vehicle.brand,
        'model': vehicle.model,
        'year': vehicle.year,
        'mileage': vehicle.mileage,
        'is_listed': vehicle.listing is not None,
        "listing_status": sale_status,
        "is_auctioned" : is_auctioned_status,
        "auction_status_resource": auction_status_resource.get("auction_status_resource") if auction_status_resource else None
    }

def serialize_battery(battery):
    if not battery: return None 
    auction_status_resource = None
    is_auctioned_status = None
    sale_status = None
    if battery.listing:
        sale_status = battery.listing.status
    if not battery.listing:
        is_auctioned_status = is_auctioned('battery', battery.battery_id)
    if not battery.listing:
        auction_status_resource = auction_status('battery', battery.battery_id)

    return {
        'battery_id': battery.battery_id,
        'user_id': battery.user_id,
        'manufacturer': battery.manufacturer,
        'capacity_kwh': battery.capacity_kwh,
        'health_percent': battery.health_percent,
        'is_listed': battery.listing is not None,
        "listing_status": sale_status,
        "is_auctioned" : is_auctioned_status,
        "auction_status_resource": auction_status_resource.get("auction_status_resource") if auction_status_resource else None
    }


def serialize_listing(listing):
    if not listing: return None

    vehicle_details = serialize_vehicle(listing.vehicle) if hasattr(listing, 'vehicle') and listing.vehicle else None
    battery_details = serialize_battery(listing.battery) if hasattr(listing, 'battery') and listing.battery else None

    return {
    'listing_id': listing.listing_id,
    'seller_id': listing.seller_id,
    'listing_type': listing.listing_type,
    'title': listing.title,
    'description': listing.description,
    'price': str(listing.price),
    'status': listing.status,
    'created_at': listing.created_at.isoformat() if listing.created_at else None,
    'vehicle_details': vehicle_details,
    'battery_details': battery_details,
    'images': [img.image_url for img in listing.images] if hasattr(listing, 'images') and listing.images else []
    }

# ============================================
# === API QUẢN LÝ KHO (MY ASSETS) ===
# ============================================
# image
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Kiểm tra xem file có đuôi mở rộng hợp lệ không."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_bp.route("/listings/add_image_vehicle/<int:vehicle_id>", methods=["POST"])
@jwt_required()
def add_image_vehicle(vehicle_id): 
    current_user_id = int(get_jwt_identity())
    vehicle = VehicleService.get_vehicle_by_id(vehicle_id=vehicle_id)
    if not vehicle: return None, "Vehicle not found"
    listing = ListingService.get_listing_by_vehicle_id(vehicle_id)
    if not listing or listing.seller_id != current_user_id:
        return jsonify({"error": "Listing not found or you don't have permission"}), 403

    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file and allowed_file(file.filename): 
        filename = secure_filename(file.filename)
        unique_filename = str(uuid.uuid4()) + "_" + filename 
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        old_images = ListingImage.query.filter_by(listing_id=listing.listing_id).all()
        for img in old_images:
            old_file_path = os.path.join(upload_folder, os.path.basename(img.image_url))
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
            db.session.delete(img)
        db.session.commit()

        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
 
        image_url = f"/uploads/{unique_filename}"
        new_image = ListingImage(listing_id=listing.listing_id, image_url=image_url)
        db.session.add(new_image)
        db.session.commit()
        
        return jsonify({
            "message": "Image uploaded successfully", 
            "image": {"image_id": new_image.image_id, "image_url": new_image.image_url}
        }), 201
    
    return jsonify({"error": "File type not allowed"}), 400

@api_bp.route("/listings/add_image_battery/<int:battery_id>", methods=["POST"])
@jwt_required()
def add_image_battery_(battery_id): 
    current_user_id = int(get_jwt_identity())
    battery = BatteryService.get_battery_by_id(battery_id=battery_id)
    if not battery: return None, "battery not found"
    listing = ListingService.get_listing_by_battery_id(battery_id)
    if not listing or listing.seller_id != current_user_id:
        return jsonify({"error": "Listing not found or you don't have permission"}), 403

    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file and allowed_file(file.filename): 
        filename = secure_filename(file.filename)
        unique_filename = str(uuid.uuid4()) + "_" + filename 
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        old_images = ListingImage.query.filter_by(listing_id=listing.listing_id).all()
        for img in old_images:
            old_file_path = os.path.join(upload_folder, os.path.basename(img.image_url))
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
            db.session.delete(img)
        db.session.commit()
        
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
 
        image_url = f"/uploads/{unique_filename}"
        new_image = ListingImage(listing_id=listing.listing_id, image_url=image_url)
        db.session.add(new_image)
        db.session.commit()

        return jsonify({
            "message": "Image updated successfully",
            "image": {"image_id": new_image.image_id, "image_url": new_image.image_url}
        }), 201

    return jsonify({"error": "File type not allowed"}), 400

# --- BATTERY INVENTORY ---
@api_bp.route("/my-assets/batteries", methods=["GET"])
@jwt_required()
def get_my_batteries():
    current_user_id = int(get_jwt_identity())
    batteries = BatteryService.get_batteries_by_user_id(current_user_id)
    return jsonify([serialize_battery(b) for b in batteries]), 200

@api_bp.route("/my-assets/batteries", methods=["POST"])
@jwt_required()
def add_battery_to_my_inventory():
    current_user_id = int(get_jwt_identity())
    battery, message = BatteryService.create_battery(current_user_id, request.get_json())
    if not battery: return jsonify({"error": message}), 400
    return jsonify({"message": message, "battery": serialize_battery(battery)}), 201

@api_bp.route("/my-assets/batteries/<int:battery_id>", methods=["PUT"])
@jwt_required()
def update_my_battery(battery_id):
    current_user_id = int(get_jwt_identity())
    battery, message = BatteryService.update_battery(battery_id, current_user_id, request.get_json())
    if not battery: return jsonify({"error": message}), 404
    return jsonify({"message": message, "battery": serialize_battery(battery)}), 200

@api_bp.route("/my-assets/batteries/<int:battery_id>", methods=["DELETE"])
@jwt_required()
def delete_my_battery(battery_id):
    current_user_id = int(get_jwt_identity())
    success, message = BatteryService.delete_battery(battery_id, current_user_id)
    if not success: return jsonify({"error": message}), 400
    return jsonify({"message": message}), 200

# --- VEHICLE INVENTORY ---
@api_bp.route("/my-assets/vehicles", methods=["GET"])
@jwt_required()
def get_my_vehicles():
    current_user_id = int(get_jwt_identity())
    vehicles = VehicleService.get_vehicles_by_user_id(current_user_id)
    return jsonify([serialize_vehicle(v) for v in vehicles]), 200

@api_bp.route("/my-assets/vehicles", methods=["POST"])
@jwt_required()
def add_vehicle_to_inventory():
    current_user_id = int(get_jwt_identity())
    vehicle, message = VehicleService.create_vehicle(current_user_id, request.get_json())
    if not vehicle: return jsonify({"error": message}), 400
    return jsonify({"message": message, "vehicle": serialize_vehicle(vehicle)}), 201

@api_bp.route("/my-assets/vehicles/<int:vehicle_id>", methods=["PUT"])
@jwt_required()
def update_my_vehicle(vehicle_id):
    current_user_id = int(get_jwt_identity())
    vehicle, message = VehicleService.update_vehicle(vehicle_id, current_user_id, request.get_json())
    if not vehicle: return jsonify({"error": message}), 404
    return jsonify({"message": message, "vehicle": serialize_vehicle(vehicle)}), 200

@api_bp.route("/my-assets/vehicles/<int:vehicle_id>", methods=["DELETE"])
@jwt_required()
def delete_my_vehicle(vehicle_id):
    current_user_id = int(get_jwt_identity())
    success, message = VehicleService.delete_vehicle(vehicle_id, current_user_id)
    if not success: return jsonify({"error": message}), 400
    return jsonify({"message": message}), 200

# ============================================
# === API ĐĂNG BÁN / GỠ BÁN (MY ASSETS) ===
# ============================================

@api_bp.route("/my-assets/batteries/<int:battery_id>/list", methods=["POST"])
@jwt_required()
def post_my_battery_for_sale(battery_id):
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    if not data or not all(k in data for k in ['title', 'price', 'description']):
        return jsonify({"error": "Missing listing data: title, price, description are required."}), 400
    listing, message = BatteryService.post_battery_to_listing(current_user_id, battery_id, data)
    if not listing: return jsonify({"error": message}), 400
    return jsonify({
        "message": message, 
        "listing": serialize_listing(listing)
        }), 201

@api_bp.route("/my-assets/batteries/<int:battery_id>/list", methods=["DELETE"])
@jwt_required()
def remove_my_battery_from_sale(battery_id):
    current_user_id = int(get_jwt_identity())
    claims = get_jwt()
    current_user_role = claims.get("role")
 
    listing = ListingService.get_listing_by_battery_id(battery_id)
    if not listing:
        return jsonify({"error": "Không tìm thấy tin đăng nào cho pin này."}), 404
 
    if listing.seller_id != current_user_id and current_user_role != 'admin':
         return jsonify({"error": "Bạn không có quyền gỡ tin đăng này."}), 403
 
    try:
        has_tx, tx_status = has_active_transaction(listing.listing_id)
        if has_tx:
            logger.warning(f"Từ chối gỡ: User {current_user_id} cố gỡ Listing (Pin) {listing.listing_id} đã có giao dịch (Status: {tx_status}).")
            return jsonify({"error": f"Không thể gỡ tin đăng này vì đã phát sinh giao dịch (trạng thái: {tx_status})."}), 400
    
    except Exception as e:
        logger.error(f"Lỗi khi kiểm tra giao dịch của listing (Pin) {listing.listing_id}: {e}")
        return jsonify({"error": "Lỗi máy chủ khi kiểm tra giao dịch."}), 500
     
    success, message = BatteryService.remove_battery_from_listing(current_user_id, current_user_role, battery_id)
    if not success: 
        return jsonify({"error": message}), 404 
    
    return jsonify({"message": message}), 200

@api_bp.route("/my-assets/vehicles/<int:vehicle_id>/list", methods=["POST"])
@jwt_required()
def post_my_vehicle_for_sale(vehicle_id):
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    if not data or not all(k in data for k in ['title', 'price', 'description']):
        return jsonify({"error": "Missing listing data: title, price, description are required."}), 400
    listing, message = VehicleService.post_vehicle_to_listing(current_user_id, vehicle_id, data)
    if not listing: return jsonify({"error": message}), 400
    return jsonify({"message": message, "listing": serialize_listing(listing)}), 201

@api_bp.route("/my-assets/vehicles/<int:vehicle_id>/list", methods=["DELETE"])
@jwt_required()
def remove_my_vehicle_from_sale(vehicle_id):
    current_user_id = int(get_jwt_identity())
    claims = get_jwt()
    current_user_role = claims.get("role")
 
    listing = ListingService.get_listing_by_vehicle_id(vehicle_id)
    if not listing:
        return jsonify({"error": "Không tìm thấy tin đăng nào cho xe này."}), 404
 
    if listing.seller_id != current_user_id and current_user_role != 'admin':
         return jsonify({"error": "Bạn không có quyền gỡ tin đăng này."}), 403
 
    try:
        has_tx, tx_status = has_active_transaction(listing.listing_id)
        if has_tx:
            logger.warning(f"Từ chối gỡ: User {current_user_id} cố gỡ Listing (Xe) {listing.listing_id} đã có giao dịch (Status: {tx_status}).")
            return jsonify({"error": f"Không thể gỡ tin đăng này vì đã phát sinh giao dịch (trạng thái: {tx_status})."}), 400
    
    except Exception as e:
        logger.error(f"Lỗi khi kiểm tra giao dịch của listing (Xe) {listing.listing_id}: {e}")
        return jsonify({"error": "Lỗi máy chủ khi kiểm tra giao dịch."}), 500
     
    success, message = VehicleService.remove_vehicle_from_listing(current_user_id, current_user_role, vehicle_id)
    if not success: 
        return jsonify({"error": message}), 404  

    return jsonify({"message": message}), 200
 
# ============================================
# === API watch list ===
# ============================================
@api_bp.route("/watch-list", methods=['POST'])
@jwt_required()
def add_to_watchlist():
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    listing_id = data.get("listing_id")
    watchlist, message = ListingService.add_to_watchlist(current_user_id, listing_id)
    if not watchlist:
        return jsonify({"error": message}), 400
    return jsonify({"message": message}), 200

@api_bp.route("/watch-list", methods = ['GET'])
@jwt_required()
def my_watchlist():
    current_user_id = int(get_jwt_identity())
    watchlists = ListingService.get_watchlist(current_user_id)
    return jsonify([serialize_listing(w) for w in watchlists]), 200

@api_bp.route("/watch-list/by-listing/<int:listing_id>", methods=['DELETE'])
@jwt_required()
def delete_watchlist_by_listing(listing_id):
    current_user_id = int(get_jwt_identity())     
    watchlist_item = WatchList.query.filter_by(
        user_id=current_user_id, 
        listing_id=listing_id
    ).first()
    
    if not watchlist_item: 
        return jsonify({"message": "Tin đăng này không có trong danh sách theo dõi."}), 404
    success, message = ListingService.remove_from_watchlist(watchlist_item.watchlist_id)
    if not success:
         return jsonify({"message": message}), 400 
    return jsonify({"message": "Đã xóa khỏi danh sách theo dõi"}), 200

# ============================================
# === CÁC API CÔNG KHAI (PUBLIC) ===
# ============================================
@api_bp.route('/listings', methods=['GET'])
def search_listings():
    listings = ListingService.get_all_listings() 
    return jsonify([serialize_listing(l) for l in listings]), 200

@api_bp.route('/listings/filter', methods=['GET'])
def filter_listings():
    filters = {
        "listing_type": request.args.get("listing_type"),
        "title": request.args.get("title"),
        "min_price": request.args.get("min_price"),
        "max_price": request.args.get("max_price"),

        "brand": request.args.get("brand"),
        "model": request.args.get("model"),
        "year": request.args.get("year"),
        "mileage_min": request.args.get("mileage_min"),
        "mileage_max": request.args.get("mileage_max"),

        "manufacturer": request.args.get("manufacturer"),
        "capacity_min": request.args.get("capacity_min"),
        "capacity_max": request.args.get("capacity_max"),
        "health_min": request.args.get("health_min"),
        "health_max": request.args.get("health_max"),
    }
    try:
        listings = ListingService.filter_listings(filters)
        return jsonify([serialize_listing(l) for l in listings]), 200
    except Exception as e:
        print("❌ Lỗi khi lọc listings:", e)
        return jsonify({"error": "Lỗi khi lọc dữ liệu", "message": str(e)}), 500

@api_bp.route('/listings/<int:listing_id>', methods=['GET'])
def get_listing_details(listing_id):
    listing = ListingService.get_listing_by_id(listing_id)
    if not listing: return jsonify({"error": "Listing not found"}), 404
    return jsonify(serialize_listing(listing)), 200

@api_bp.route('/listings/vehicle/<int:vehicle_id>', methods=['GET'])
def get_vehicle_details(vehicle_id):
    vehicle = VehicleService.get_vehicle_by_id(vehicle_id)
    if not vehicle: return jsonify({"error": "Vehicle not found"}), 404
    listing = ListingService.get_listing_by_vehicle_id(vehicle_id=vehicle_id)
    if not listing: return jsonify({"error": "Listing not found"}), 404
    return jsonify(serialize_listing(listing)), 200

@api_bp.route('/listings/battery/<int:battery_id>', methods=['GET'])
def get_battery_details(battery_id):
    battery = BatteryService.get_battery_by_id(battery_id)
    if not battery: return jsonify({"error": "battery not found"}), 404
    listing = ListingService.get_listing_by_battery_id(battery_id)
    if not listing: return jsonify({"error": "Listing not found"}), 404
    return jsonify(serialize_listing(listing)), 200

# ============================================
# === API ===
# ============================================

@api_bp.route('/listings/<int:listing_id>', methods=['PUT'])
@jwt_required()
def update_listing(listing_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    if not data: return jsonify({"error": "Request body must be JSON"}), 400
    listing, message = ListingService.update_listing(listing_id, user_id, data)
    if not listing:
        return jsonify({"error": message}), 403
    return jsonify({"message": message, "listing": serialize_listing(listing)}), 200

@api_bp.route('/listings/<int:listing_id>', methods=['DELETE'])
@jwt_required()
def remove_listing(listing_id):
    user_id = int(get_jwt_identity())
    user_role = get_jwt().get('role')
    try:
        has_tx, tx_status = has_active_transaction(listing_id)
        if has_tx: 
            logger.warning(f"Từ chối xóa: User {user_id} (Role: {user_role}) cố xóa Listing {listing_id} đã có giao dịch (Status: {tx_status}).")
            return jsonify({"error": f"Không thể xóa tin đăng này vì đã phát sinh giao dịch (trạng thái: {tx_status})."}), 400 # 400 Bad Request
    
    except Exception as e:
        logger.error(f"Lỗi nghiêm trọng khi kiểm tra giao dịch của listing {listing_id}: {e}")
        return jsonify({"error": "Lỗi máy chủ khi kiểm tra giao dịch."}), 500 
    success, message = ListingService.delete_listing(listing_id, user_id, user_role)
    if not success:  
        status_code = 403 if "quyền" in message.lower() else 404
        return jsonify({"error": message}), status_code
    
    return jsonify({"message": message}), 200

# ================================

@api_bp.route('/vehicles/<int:vehicle_id>', methods=['GET'])
def get_raw_vehicle_details(vehicle_id):
    vehicle = VehicleService.get_vehicle_by_id(vehicle_id)
    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404 
    return jsonify(_serialize_vehicle_basic(vehicle)), 200

@api_bp.route('/batteries/<int:battery_id>', methods=['GET'])
def get_raw_battery_details(battery_id):
     battery = BatteryService.get_battery_by_id(battery_id)
     if not battery:
         return jsonify({"error": "Battery not found"}), 404 
     return jsonify(_serialize_battery_basic(battery)), 200

@api_bp.route('/listings/<int:listing_id>/status', methods=['PUT'])
@service_or_user_required()
def update_listing_status(listing_id):
    data = request.get_json()
    new_status = data.get('status')
    if not new_status: return jsonify({"error": "Missing 'status' in request body"}), 400
        
    listing, message = ListingService.update_listing_status(listing_id, new_status)
    if not listing: return jsonify({"error": message}), 404
        
    return jsonify({"message": message, "listing": serialize_listing(listing)}), 200






