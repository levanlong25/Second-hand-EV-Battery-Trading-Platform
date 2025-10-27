# controllers/review_controller.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.review_service import ReviewService # Import service logic
# Import db để dùng session nếu cần rollback (hoặc để service tự quản lý)
# from app import db
import logging

logger = logging.getLogger(__name__)

# Đổi tên Blueprint và prefix
review_api = Blueprint('review_api', __name__, url_prefix='/api')

# --- Hàm Helper Serialize ---
def serialize_review(review):
    if not review: return None
    return {
        'review_id': review.review_id,
        'transaction_id': review.transaction_id,
        'reviewer_id': review.reviewer_id,
        'reviewed_user_id': review.reviewed_user_id,
        'rating': review.rating,
        'comment': review.comment,
        'created_at': review.created_at.isoformat() if review.created_at else None
        # Có thể thêm username người đánh giá/được đánh giá bằng cách gọi User Service nếu cần
    }

# --- API Endpoints ---

@review_api.route('/reviews', methods=['POST'])
@jwt_required() # Yêu cầu token JWT hợp lệ
def create_review_api():
    """Tạo một đánh giá mới."""
    try:
        reviewer_id = int(get_jwt_identity()) # Lấy ID người dùng từ token
    except (ValueError, TypeError):
         return jsonify(error="User ID không hợp lệ trong token"), 401

    data = request.get_json()
    if not data:
        return jsonify(error="Thiếu JSON body"), 400

    # Lấy dữ liệu từ JSON body
    transaction_id = data.get('transaction_id')
    reviewed_user_id = data.get('reviewed_user_id')
    rating = data.get('rating')
    comment = data.get('comment') # Comment có thể null

    # Kiểm tra các trường bắt buộc
    if not all([transaction_id, reviewed_user_id, rating is not None]):
         return jsonify(error="Thiếu các trường bắt buộc: transaction_id, reviewed_user_id, rating"), 400

    try:
        # Gọi service để tạo review
        review, error_message = ReviewService.create_review(
            transaction_id=transaction_id,
            reviewer_id=reviewer_id,
            reviewed_user_id=reviewed_user_id,
            rating=rating,
            comment=comment
        )

        if not review:
            # Kiểm tra lỗi trùng lặp hay lỗi khác
            status_code = 409 if "đã tồn tại" in (error_message or "") else 400
            return jsonify(error=error_message or "Không thể tạo đánh giá."), status_code

        # Trả về review vừa tạo
        return jsonify(review=serialize_review(review)), 201 # 201 Created

    except ValueError as ve: # Bắt lỗi validation rating từ service/model
         return jsonify(error=str(ve)), 400
    except Exception as e:
        logger.error(f"Lỗi khi tạo review: {e}", exc_info=True)
        return jsonify(error="Lỗi máy chủ nội bộ khi tạo đánh giá."), 500


@review_api.route('/reviews/<int:review_id>', methods=['PUT'])
@jwt_required()
def update_review_api(review_id):
    """Cập nhật đánh giá (chỉ người tạo mới được sửa)."""
    try:
        user_id = int(get_jwt_identity())
    except (ValueError, TypeError):
         return jsonify(error="User ID không hợp lệ trong token"), 401

    data = request.get_json()
    if not data:
        return jsonify(error="Thiếu JSON body"), 400

    rating = data.get('rating') # Có thể chỉ cập nhật rating
    comment = data.get('comment') # Hoặc chỉ comment

    if rating is None and comment is None:
        return jsonify(error="Phải cung cấp rating hoặc comment để cập nhật."), 400

    try:
        updated_review, error_message = ReviewService.update_review(
            review_id=review_id,
            user_id=user_id, # Truyền user_id để kiểm tra quyền
            rating=rating,
            comment=comment
        )

        if not updated_review:
            # Kiểm tra lỗi quyền hay lỗi không tìm thấy
            status_code = 403 if "quyền" in (error_message or "") else 404
            return jsonify(error=error_message or "Không thể cập nhật đánh giá."), status_code

        return jsonify(review=serialize_review(updated_review)), 200

    except ValueError as ve: # Bắt lỗi validation rating
         return jsonify(error=str(ve)), 400
    except Exception as e:
        logger.error(f"Lỗi khi cập nhật review {review_id}: {e}", exc_info=True)
        return jsonify(error="Lỗi máy chủ nội bộ khi cập nhật đánh giá."), 500


@review_api.route('/reviews/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review_api(review_id):
    """Xóa đánh giá (chỉ người tạo mới được xóa)."""
    try:
        user_id = int(get_jwt_identity())
    except (ValueError, TypeError):
         return jsonify(error="User ID không hợp lệ trong token"), 401

    try:
        success, message = ReviewService.delete_review(
            review_id=review_id,
            user_id=user_id # Truyền user_id để kiểm tra quyền
        )

        if not success:
            status_code = 403 if "quyền" in (message or "") else 404
            return jsonify(error=message or "Không thể xóa đánh giá."), status_code

        return jsonify(message=message), 200 # Hoặc 204 No Content

    except Exception as e:
        logger.error(f"Lỗi khi xóa review {review_id}: {e}", exc_info=True)
        return jsonify(error="Lỗi máy chủ nội bộ khi xóa đánh giá."), 500


@review_api.route('/reviews/user/<int:user_id>', methods=['GET'])
# Bỏ @jwt_required() nếu muốn public, thêm nếu cần đăng nhập để xem
def get_reviews_for_user_api(user_id):
    """Lấy tất cả đánh giá VỀ một người dùng."""
    try:
        reviews = ReviewService.get_reviews_by_user(user_id)
        # Serialize danh sách reviews
        return jsonify([serialize_review(r) for r in reviews]), 200
    except Exception as e:
         logger.error(f"Lỗi khi lấy reviews cho user {user_id}: {e}", exc_info=True)
         return jsonify(error="Lỗi máy chủ nội bộ khi lấy đánh giá."), 500

@review_api.route('/reviews/my-reviews', methods=['GET'])  
@jwt_required()
def get_my_reviews_api():  
    """Lấy tất cả đánh giá DO người dùng hiện tại viết."""
    try:
        reviewer_id = int(get_jwt_identity())  
    except (ValueError, TypeError):
         return jsonify(error="User ID không hợp lệ trong token"), 401
    
    try:
        reviews = ReviewService.get_reviews_by_reviewer(reviewer_id)  
        return jsonify([serialize_review(r) for r in reviews]), 200
    except Exception as e:
         logger.error(f"Lỗi khi lấy reviews của user {reviewer_id}: {e}", exc_info=True)
         return jsonify(error="Lỗi máy chủ nội bộ khi lấy đánh giá."), 500

@review_api.route('/reviews/transaction/<int:transaction_id>', methods=['GET'])
def get_reviews_for_transaction_api(transaction_id):
    """Lấy tất cả đánh giá CỦA một giao dịch."""
    try:
        reviews = ReviewService.get_reviews_by_transaction(transaction_id)
        return jsonify([serialize_review(r) for r in reviews]), 200
    except Exception as e:
         logger.error(f"Lỗi khi lấy reviews cho transaction {transaction_id}: {e}", exc_info=True)
         return jsonify(error="Lỗi máy chủ nội bộ khi lấy đánh giá."), 500
     
@review_api.route('/reviews/<int:review_id>', methods=['GET'])  
@jwt_required()
def get_review_by_id_api(review_id):
    """Lấy chi tiết một review (để sửa)."""
    try:
        user_id = int(get_jwt_identity())
    except (ValueError, TypeError):
         return jsonify(error="User ID không hợp lệ trong token"), 401
         
    try:
        review = ReviewService.get_review_by_id_and_reviewer(review_id, user_id)
        if not review:
            return jsonify(error="Không tìm thấy đánh giá hoặc bạn không có quyền sửa."), 404
        return jsonify(serialize_review(review)), 200
    except Exception as e:
         logger.error(f"Lỗi khi lấy review {review_id}: {e}", exc_info=True)
         return jsonify(error="Lỗi máy chủ nội bộ."), 500