# transaction-service/controllers/internal_controller.py
from functools import wraps
from flask import Blueprint, jsonify, request, current_app
import os
import logging
from app import db # Import db instance
from models.payment import Payment
from models.transaction import Transaction # Cần Transaction để Join
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
    """Admin service gọi để lấy tất cả payment (join transaction)."""
    try:
        # Query giống như get_all_payments_admin cũ
        all_payments = (
            db.session.query(Payment)
            .join(Transaction, Payment.transaction_id == Transaction.transaction_id) # Join để lấy buyer/seller_id
             # .options(joinedload(Payment.transaction)) # Eager load nếu cần nhiều thông tin transaction
            .order_by(Payment.created_at.desc())
            .all()
        )
        # Serialize dùng hàm đã có (hàm này sẽ gọi user-service để lấy username)
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