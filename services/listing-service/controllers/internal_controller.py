# listing-service/controllers/internal_controller.py
from functools import wraps
from flask import Blueprint, jsonify, request, current_app
import os
import logging 
from services.listing_service import ListingService 
from .listing_controller import serialize_listing  

internal_bp = Blueprint('internal_api', __name__, url_prefix='/internal')
logger = logging.getLogger(__name__)

# --- Decorator Kiểm Tra API Key Nội Bộ (Copy từ user-service/internal_controller.py) ---
def internal_api_key_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            provided_key = request.headers.get('X-Internal-Api-Key') # Key từ NiFi
            correct_key = os.environ.get('INTERNAL_API_KEY')       # Key từ .env
            
            # --- (THÊM 2 DÒNG LOG DEBUG) ---
            logger.warning(f"DEBUG: Key Python đọc từ .env:  '[{correct_key}]'")
            logger.warning(f"DEBUG: Key NiFi gửi đến     : '[{provided_key}]'")
            # --- (KẾT THÚC THÊM LOG) ---

            if not correct_key:
                logger.error("INTERNAL_API_KEY chưa được cấu hình!")
                return jsonify(error="Lỗi cấu hình server"), 500
            
            if provided_key and provided_key == correct_key:
                return fn(*args, **kwargs)
            else:
                logger.warning(f"Từ chối truy cập internal API (Listing): Sai API Key.")
                return jsonify(error="Unauthorized internal access"), 403
        return decorator
    return wrapper

# --- Các Endpoint Nội Bộ cho Listing ---

@internal_bp.route("/listings", methods=["GET"])
@internal_api_key_required()
def internal_get_all_listings():
    """Admin service gọi để lấy tất cả listing (có lọc)."""
    status = request.args.get('status')
    listing_type = request.args.get('type') 
    
    listings = ListingService.get_absolutely_all_listings()

    try:
        if status:
            listings = [l for l in listings if l.status == status]
        if listing_type: 
            listings = [l for l in listings if l.listing_type == listing_type]
    except AttributeError:
         logger.error("Lỗi khi lọc listing: đối tượng thiếu 'status' hoặc 'listing_type'.")
         pass

    return jsonify([serialize_listing(l) for l in listings]), 200


@internal_bp.route("/listings/pending", methods=["GET"])
@internal_api_key_required()
def internal_get_pending_listings():
    """Admin service gọi để lấy listing chờ duyệt."""
    listings = ListingService.get_pending_listings()
    return jsonify([serialize_listing(l) for l in listings]), 200

@internal_bp.route("/listings/<int:listing_id>/status", methods=["PUT"])
@internal_api_key_required()
def internal_update_listing_status(listing_id):
    """Admin service gọi để cập nhật status (available, rejected, sold...)."""
    data = request.get_json()
    new_status = data.get('status')
    if not new_status: return jsonify(error="Missing 'status' in request body"), 400 
    listing, message = ListingService.update_listing_status(listing_id, new_status)
    if not listing: return jsonify(error=message), 404 # Hoặc 400 tùy lỗi

    return jsonify(message=message, listing=serialize_listing(listing)), 200

@internal_bp.route('/listings/<int:listing_id>', methods=['DELETE'])
@internal_api_key_required()
def internal_delete_listing(listing_id):
    """Admin service gọi để xóa listing (admin có quyền xóa mọi listing).""" 
    success, message = ListingService.delete_listing(listing_id)  

    if not success: return jsonify(error=message), 404  
    return jsonify(message=message), 200