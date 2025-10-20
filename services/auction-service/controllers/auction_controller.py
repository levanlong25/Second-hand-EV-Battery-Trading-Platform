from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.auction_service import AuctionService
from models.listing import Listing
from datetime import datetime, timezone

# Định nghĩa Blueprint ngay tại đây
api_auction_bp = Blueprint("api_auction", __name__, url_prefix="/api/auctions")

def serialize_auction(auction):
    """Hàm chuyển đổi object Auction thành dictionary."""
    return {
        "auction_id": auction.auction_id,
        "listing_id": auction.listing_id,
        "start_time": auction.start_time.isoformat(),
        "end_time": auction.end_time.isoformat(),
        "current_bid": float(auction.current_bid),
        "winning_bidder_id": auction.winning_bidder_id,
        "status": auction.status
    }

@api_auction_bp.route("/", methods=["POST"])
@jwt_required()
def create_auction():
    data = request.get_json()
    required_fields = ["listing_id", "start_time", "end_time", "starting_bid"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Thiếu thông tin bắt buộc."}), 400

    # Kiểm tra listing có tồn tại và thuộc về user không
    user_id = get_jwt_identity()
    listing = Listing.query.get(data['listing_id'])
    if not listing or listing.seller_id != user_id:
        return jsonify({"error": "Bạn không có quyền với sản phẩm này."}), 403

    # Chuyển đổi chuỗi thời gian sang datetime object
    try:
        data['start_time'] = datetime.fromisoformat(data['start_time'])
        data['end_time'] = datetime.fromisoformat(data['end_time'])
    except ValueError:
        return jsonify({"error": "Định dạng thời gian không hợp lệ."}), 400

    auction, message = AuctionService.create_auction(data)
    if not auction:
        return jsonify({"error": message}), 500
    return jsonify({"message": message, "auction": serialize_auction(auction)}), 201

@api_auction_bp.route("/<int:auction_id>", methods=["PUT"])
@jwt_required()
def update_auction(auction_id):
    auction = AuctionService.get_auction_by_id(auction_id)
    if not auction:
        return jsonify({"error": "Không tìm thấy phiên đấu giá."}), 404
    
    # Yêu cầu: Sửa phải sửa trước thời gian bắt đầu
    if datetime.now(timezone.utc) >= auction.start_time:
        return jsonify({"error": "Không thể sửa phiên đấu giá đã hoặc đang diễn ra."}), 403
        
    data = request.get_json()
    updated_auction, message = AuctionService.update_auction(auction, data)
    if not updated_auction:
        return jsonify({"error": message}), 500
    return jsonify({"message": message, "auction": serialize_auction(updated_auction)}), 200

@api_auction_bp.route("/<int:auction_id>", methods=["DELETE"])
@jwt_required()
def delete_auction(auction_id):
    auction = AuctionService.get_auction_by_id(auction_id)
    if not auction:
        return jsonify({"error": "Không tìm thấy phiên đấu giá."}), 404
        
    success, message = AuctionService.delete_auction(auction)
    if not success:
        return jsonify({"error": message}), 500
    return jsonify({"message": message}), 200

@api_auction_bp.route("/<int:auction_id>/bid", methods=["POST"])
@jwt_required()
def place_bid(auction_id):
    auction = AuctionService.get_auction_by_id(auction_id)
    if not auction:
        return jsonify({"error": "Không tìm thấy phiên đấu giá."}), 404
    
    if auction.status != "Đang diễn ra":
        return jsonify({"error": "Phiên đấu giá không hoạt động."}), 400

    data = request.get_json()
    bid_amount = data.get("bid_amount")
    if bid_amount is None or float(bid_amount) <= float(auction.current_bid):
        return jsonify({"error": f"Giá đặt phải lớn hơn giá hiện tại ({auction.current_bid})."}), 400
        
    bidder_id = get_jwt_identity()
    updated_auction, message = AuctionService.place_bid(auction, bidder_id, bid_amount)
    if not updated_auction:
        return jsonify({"error": message}), 500
    return jsonify({"message": message, "auction": serialize_auction(updated_auction)}), 200

@api_auction_bp.route("/filter/active", methods=["GET"])
def filter_active_auctions():
    auctions = AuctionService.filter_active_auctions()
    return jsonify([serialize_auction(a) for a in auctions]), 200

@api_auction_bp.route("/filter/type/<string:listing_type>", methods=["GET"])
def filter_auctions_by_type(listing_type):
    auctions = AuctionService.filter_auctions_by_type(listing_type)
    return jsonify([serialize_auction(a) for a in auctions]), 200