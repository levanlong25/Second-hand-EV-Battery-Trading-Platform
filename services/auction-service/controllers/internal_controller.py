from functools import wraps
from flask import Blueprint, jsonify, request, current_app
import os
import logging 
from services.auction_service import AuctionService 
from .auction_controller import serialize_auction  

internal_bp = Blueprint('internal_api', __name__, url_prefix='/internal')
logger = logging.getLogger(__name__)

# --- Decorator Kiểm Tra API Key Nội Bộ (Copy từ service khác) ---
def internal_api_key_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            provided_key = request.headers.get('X-Internal-Api-Key')
            correct_key = os.environ.get('INTERNAL_API_KEY')
            if not correct_key:
                 logger.error("INTERNAL_API_KEY chưa được cấu hình!")
                 return jsonify(error="Lỗi cấu hình server"), 500
            if provided_key and provided_key == correct_key:
                return fn(*args, **kwargs)
            else:
                logger.warning(f"Từ chối truy cập internal API (Auction): Sai API Key.")
                return jsonify(error="Unauthorized internal access"), 403
        return decorator
    return wrapper
 
@internal_bp.route("/auctions", methods=["GET"])
@internal_api_key_required()
def internal_get_all_auctions():
    """Admin service gọi để lấy tất cả auction (có lọc).""" 
    auction_status = request.args.get('auction_status')            
    auction_type = request.args.get('auction_type')          

    auctions = AuctionService.get_absolutely_all_auctions()
 
    if auction_status:
        auctions = [a for a in auctions if a.auction_status.lower() == auction_status.lower()]
    
    if auction_type:
        auctions = [a for a in auctions if a.auction_type.lower() == auction_type.lower()]

    return jsonify([serialize_auction(a) for a in auctions]), 200


@internal_bp.route("/auctions/pending", methods=["GET"])
@internal_api_key_required()
def internal_get_pending_auctions():
    """Admin service gọi để lấy auction chờ duyệt."""
    auctions = AuctionService.get_pending_auctions()  
    return jsonify([serialize_auction(a) for a in auctions]), 200

@internal_bp.route("/auctions/<int:auction_id>/finalize", methods=["PUT"])
@internal_api_key_required()
def internal_finalize_auction(auction_id):
    """Admin service gọi để kết thúc auction thủ công."""
    auction, message = AuctionService.manually_finalize_auction(auction_id)
    if not auction:
        return jsonify(error=message), 400 # Hoặc 404
    return jsonify(message=message, auction=serialize_auction(auction)), 200

@internal_bp.route("/auctions/review", methods=["POST"])
@internal_api_key_required()
def internal_review_auction():
    """Admin service gọi để duyệt/từ chối auction."""
    data = request.get_json()
    if not data or 'auction_id' not in data or data.get('approve') is None:
        return jsonify(error="Thiếu auction_id hoặc approve (true/false)"), 400
    auction_id = data.get('auction_id')
    is_approved = bool(data.get('approve'))
    auction, message = AuctionService.review_auction(auction_id, is_approved)
    if not auction:
        return jsonify(error=message), 400  
    return jsonify(message=message, auction=serialize_auction(auction)), 200

@internal_bp.route("/auctions/<int:auction_id>/status", methods=["PUT"])
@internal_api_key_required()
def internal_update_auction_status(auction_id):
    """Admin service gọi để cập nhật status bất kỳ (cẩn thận khi dùng)."""
    data = request.get_json()
    new_status = data.get('auction_status')  
    if not new_status: return jsonify(error="Thiếu 'auction_status'"), 400 
    auction, message = AuctionService.update_auction_status(auction_id, new_status)
    if not auction: return jsonify(error=message), 404  
    return jsonify(message=message, auction=serialize_auction(auction)), 200
 
@internal_bp.route('/auctions/<int:auction_id>', methods=['DELETE'])
@internal_api_key_required()
def internal_delete_auction(auction_id):
    """Admin service gọi để xóa auction.""" 
    success, message = AuctionService.delete_auction(auction_id, user_id=None, user_role='admin')  
    if not success: return jsonify(error=message), 404  
    return jsonify(message=message), 200