from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from services.listing_service import ListingService
from services.vehicle_service import VehicleService
from services.battery_service import BatteryService
from models.listing_image import ListingImage
from models.listing import Listing
from werkzeug.utils import secure_filename
from functools import wraps
from app import db
import uuid
import os
 
# --- Blueprint DUY NHẤT cho toàn bộ service ---
api_bp = Blueprint('api', __name__, url_prefix='/api')



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

# --- HELPER FUNCTIONS ---
def serialize_vehicle(vehicle):
    if not vehicle: return None
    return {
        'vehicle_id': vehicle.vehicle_id,
        'user_id': vehicle.user_id,
        'brand': vehicle.brand,
        'model': vehicle.model,
        'year': vehicle.year,
        'mileage': vehicle.mileage,
        'is_listed': vehicle.listing is not None,
        "listing_status": vehicle.listing.status if vehicle.listing else None
    }

def serialize_battery(battery):
    if not battery: return None
    return {
        'battery_id': battery.battery_id,
        'user_id': battery.user_id,
        'manufacturer': battery.manufacturer,
        'capacity_kwh': battery.capacity_kwh,
        'health_percent': battery.health_percent,
        'is_listed': battery.listing is not None ,
        "listing_status": battery.listing.status if battery.listing else None
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
    success, message = BatteryService.remove_battery_from_listing(current_user_id, current_user_role, battery_id)
    if not success: return jsonify({"error": message}), 404
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
    success, message = VehicleService.remove_vehicle_from_listing(current_user_id, current_user_role, vehicle_id)
    if not success: return jsonify({"error": message}), 404
    return jsonify({"message": message}), 200


# ============================================
# === CÁC API CÔNG KHAI (PUBLIC) ===
# ============================================
@api_bp.route('/listings', methods=['GET'])
def search_listings():
    listings = ListingService.get_all_listings() 
    return jsonify([serialize_listing(l) for l in listings]), 200

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
    success, message = ListingService.delete_listing(listing_id, user_id, user_role)
    if not success: return jsonify({"error": message}), 400
    return jsonify({"message": message}), 200

# ============================================
# === CÁC API ADMIN ===
# ============================================
@api_bp.route('/admin/all-listings', methods=['GET'])
@admin_required()
def get_all_listings_for_admin():
    """Lấy TOÀN BỘ tin đăng cho trang admin."""
    listings = ListingService.get_absolutely_all_listings()
    return jsonify([serialize_listing(l) for l in listings]), 200

@api_bp.route('/admin/listings/pending', methods=['GET'])
@admin_required()
def get_pending_listings_admin():
    listings = ListingService.get_pending_listings()
    return jsonify([serialize_listing(l) for l in listings]), 200

@api_bp.route('/admin/listings/<int:listing_id>/status', methods=['PUT'])
@admin_required()
def update_listing_status_admin(listing_id):
    data = request.get_json()
    new_status = data.get('status')
    if not new_status: return jsonify({"error": "Missing 'status' in request body"}), 400
        
    listing, message = ListingService.update_listing_status(listing_id, new_status)
    if not listing: return jsonify({"error": message}), 404
        
    return jsonify({"message": message, "listing": serialize_listing(listing)}), 200
