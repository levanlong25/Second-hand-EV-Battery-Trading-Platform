from functools import wraps
from flask import Blueprint, jsonify, request, current_app
import os
import logging
from services.review_service import ReviewService
from .review_controller import serialize_review # Import hàm serialize

internal_bp = Blueprint('internal_api', __name__, url_prefix='/internal')
logger = logging.getLogger(__name__)

# --- Decorator Kiểm Tra API Key Nội Bộ (Copy từ admin-service/internal_controller) ---
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
                logger.warning(f"Từ chối truy cập internal API (Review): Sai API Key.")
                return jsonify(error="Unauthorized internal access"), 403
        return decorator
    return wrapper

# === THÊM ENDPOINT NỘI BỘ MỚI ===

@internal_bp.route("/reviews/by-reviewer/<int:user_id>", methods=["GET"])
@internal_api_key_required()
def internal_get_reviews_by_reviewer(user_id):
    """API nội bộ để lấy các review do một user viết."""
    try:
        reviews = ReviewService.get_reviews_by_reviewer(user_id)
        return jsonify([serialize_review(r) for r in reviews]), 200
    except Exception as e:
         logger.error(f"Lỗi internal_get_reviews_by_reviewer cho user {user_id}: {e}", exc_info=True)
         return jsonify(error="Lỗi máy chủ nội bộ."), 500
