# transaction-service/controllers/internal_controller.py
from functools import wraps
from flask import Blueprint, jsonify, request, current_app
import os
import logging
from app import db # Import db instance
from models.payment import Payment
from models.transaction import Transaction # Cần Transaction để Join
from services.transaction_service import TransactionService
# Import các serializer cần thiết
from .transaction_controller import serialize_payment_for_admin # Import serializer admin

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
                logger.warning(f"Từ chối truy cập internal API (Transaction): Sai API Key.")
                return jsonify(error="Unauthorized internal access"), 403
        return decorator
    return wrapper

# --- Các Endpoint Nội Bộ cho Transaction/Payment ---

@internal_bp.route("/payments", methods=["GET"])
@internal_api_key_required()
def internal_get_all_payments():
    """Admin service gọi để lấy tất cả payment (join transaction và có lọc)."""
    try:
        status = request.args.get('status')  
        query = (
            db.session.query(Payment)
            .join(Transaction, Payment.transaction_id == Transaction.transaction_id) 
        ) 
        if status:
            query = query.filter(Payment.payment_status == status)
             
        all_payments = (
            query.order_by(Payment.created_at.desc())
            .all()
        ) 
        return jsonify([serialize_payment_for_admin(p) for p in all_payments]), 200
    except Exception as e:
        logger.error(f"Lỗi internal_get_all_payments: {e}", exc_info=True)
        return jsonify(error="Lỗi máy chủ nội bộ khi lấy payments."), 500


@internal_bp.route("/payments/<int:payment_id>/approve", methods=["PUT"])
@internal_api_key_required()
def internal_approve_payment(payment_id):
    """Admin service gọi để duyệt payment (pending -> completed)."""
    try:
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify(error=f"Không tìm thấy payment ID {payment_id}."), 404
        if payment.payment_status != 'pending':
            return jsonify(error=f"Payment không ở trạng thái 'pending' (hiện tại: {payment.payment_status})."), 400

        payment.payment_status = 'completed'
        db.session.commit()
        # Không cần gọi Listing service nữa vì nó đã được gọi khi status chuyển thành 'pending'
        logger.info(f"Internal API: Đã duyệt payment ID {payment_id}.")
        # Trả về thông tin payment đã cập nhật (dùng serializer thường)
        from .transaction_controller import serialize_payment # Import serializer thường
        return jsonify(message="Duyệt thanh toán thành công.", payment=serialize_payment(payment)), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Lỗi internal_approve_payment {payment_id}: {e}", exc_info=True)
        return jsonify(error="Lỗi máy chủ nội bộ khi duyệt payment."), 500
    
@internal_bp.route("/stats/kpis", methods=["GET"])
@internal_api_key_required()
def internal_get_kpis():
    """Admin service gọi để lấy các chỉ số KPI."""
    try:
        kpis, error = TransactionService.get_kpi_statistics()
        if error:
            return jsonify(error=error), 500
        return jsonify(kpis), 200
    except Exception as e:
        logger.error(f"Lỗi internal_get_kpis: {e}", exc_info=True)
        return jsonify(error="Lỗi máy chủ nội bộ."), 500


@internal_bp.route("/stats/revenue-trend", methods=["GET"])
@internal_api_key_required()
def internal_get_revenue_trend():
    """Admin service gọi để lấy xu hướng doanh thu."""
    try:
        trend, error = TransactionService.get_revenue_trend()
        if error:
            return jsonify(error=error), 500
        return jsonify(trend), 200
    except Exception as e:
        logger.error(f"Lỗi internal_get_revenue_trend: {e}", exc_info=True)
        return jsonify(error="Lỗi máy chủ nội bộ."), 500


@internal_bp.route('/check-listing-transaction/<int:listing_id>', methods=['GET'])
@internal_api_key_required()
def check_listing_transaction(listing_id):
    try:
        active_statuses = ['pending', 'awaiting_payment', 'paid']
        transaction = db.session.query(Transaction.transaction_status).filter(
            Transaction.listing_id == listing_id,
            Transaction.transaction_status.in_(active_statuses)
        ).first()

        if transaction:
            return jsonify({"has_transaction": True, "status": transaction.transaction_status}), 200
        else:
            return jsonify({"has_transaction": False}), 200

    except Exception as e:
        logger.error(f"Lỗi khi kiểm tra giao dịch cho listing {listing_id}: {e}", exc_info=True)
        return jsonify(error="Lỗi máy chủ nội bộ khi kiểm tra giao dịch."), 500
    
@internal_bp.route("/fees", methods=["GET"])
@internal_api_key_required()
def internal_get_fees():
    """Admin service gọi để lấy cấu hình phí hiện tại."""
    try:
        fee_config_dict = TransactionService.get_fee_config()
        return jsonify(fee_config_dict), 200
    except Exception as e:
        logger.error(f"Lỗi internal_get_fees: {e}", exc_info=True)
        return jsonify(error="Lỗi máy chủ nội bộ khi lấy cấu hình phí."), 500

@internal_bp.route("/fees", methods=["PUT"])
@internal_api_key_required()
def internal_update_fees(): 
    data = request.get_json()
    if not data:
        return jsonify(error="Thiếu JSON body"), 400

    listing_rate = data.get('listing_fee_rate')
    auction_rate = data.get('auction_fee_rate')

    if listing_rate is None or auction_rate is None:
        return jsonify(error="Thiếu listing_fee_rate hoặc auction_fee_rate."), 400

    try:
        updated_config, error = TransactionService.update_fee_config(listing_rate, auction_rate)
        if error:
            return jsonify(error=error), 400
        
        return jsonify(message="Cập nhật phí thành công.", fee_config=updated_config), 200
    except Exception as e:
        logger.error(f"Lỗi internal_update_fees: {e}", exc_info=True)
        return jsonify(error="Lỗi máy chủ nội bộ khi cập nhật phí."), 500
