from models.review import Review
from app import db  
import logging

logger = logging.getLogger(__name__)

class ReviewService:

    @staticmethod
    def create_review(transaction_id, reviewer_id, reviewed_user_id, rating, comment=None):
        """Tạo đánh giá mới, kiểm tra trùng lặp."""
        try:
            # --- KIỂM TRA ĐIỀU KIỆN (TÙY CHỌN NHƯNG NÊN CÓ) ---
            # 1. Kiểm tra xem người đánh giá có phải là người mua/bán của giao dịch không?
            #    (Cần gọi Transaction Service để lấy thông tin transaction)
            #    Ví dụ: transaction_info = call_transaction_service(transaction_id)
            #           if not transaction_info or reviewer_id not in [transaction_info['buyer_id'], transaction_info['seller_id']]:
            #               return None, "Bạn không tham gia giao dịch này."
            #           if reviewed_user_id not in [transaction_info['buyer_id'], transaction_info['seller_id']]:
            #                return None, "Người được đánh giá không tham gia giao dịch này."
            #           if transaction_info['transaction_status'] != 'completed': # Hoặc 'paid' tùy logic
            #                return None, "Giao dịch chưa hoàn thành để đánh giá."

            # 2. Kiểm tra xem đã đánh giá người này cho giao dịch này chưa?
            existing_review = Review.query.filter_by(
                transaction_id=transaction_id,
                reviewer_id=reviewer_id,
                reviewed_user_id=reviewed_user_id
            ).first()
            if existing_review:
                return None, "Bạn đã đánh giá người dùng này cho giao dịch này rồi."
            # --- KẾT THÚC KIỂM TRA ---


            # Chuyển đổi rating sang int (nếu cần) và kiểm tra
            try:
                rating_int = int(rating)
                if not (0 <= rating_int <= 5): # Mặc dù model có validate, check sớm hơn
                     raise ValueError("Rating phải từ 0 đến 5.")
            except (ValueError, TypeError):
                 return None, "Rating phải là một số nguyên từ 0 đến 5."

            review = Review(
                transaction_id=transaction_id,
                reviewer_id=reviewer_id,
                reviewed_user_id=reviewed_user_id,
                rating=rating_int,
                comment=comment
            )
            db.session.add(review)
            db.session.commit()
            return review, None # Trả về review và không có lỗi

        except ValueError as ve: # Lỗi validation từ model hoặc check ở trên
             return None, str(ve)
        except Exception as e:
            db.session.rollback()
            logger.error(f"Lỗi DB khi tạo review: {e}", exc_info=True)
            return None, "Lỗi cơ sở dữ liệu khi tạo đánh giá."


    @staticmethod
    def get_reviews_by_transaction(transaction_id):
        return Review.query.filter_by(transaction_id=transaction_id).all()
    
    @staticmethod
    def get_reviews_by_user(user_id):
        return Review.query.filter_by(reviewed_user_id=user_id).order_by(Review.created_at.desc()).all()

    @staticmethod
    def get_reviews_by_reviewer(reviewer_id): 
        return Review.query.filter_by(reviewer_id=reviewer_id).order_by(Review.created_at.desc()).all()

    @staticmethod
    def get_review_by_id_and_reviewer(review_id, user_id): 
        return Review.query.filter_by(review_id=review_id, reviewer_id=user_id).first()

    @staticmethod
    def delete_review(review_id, user_id):
        """Xóa đánh giá, kiểm tra quyền sở hữu."""
        review = Review.query.get(review_id)
        if not review:
            return False, "Không tìm thấy đánh giá."

        # KIỂM TRA QUYỀN: Chỉ người tạo mới được xóa
        if review.reviewer_id != user_id:
            return False, "Bạn không có quyền xóa đánh giá này."

        try:
            db.session.delete(review)
            db.session.commit()
            return True, "Đánh giá đã được xóa thành công."
        except Exception as e:
             db.session.rollback()
             logger.error(f"Lỗi DB khi xóa review {review_id}: {e}", exc_info=True)
             return False, "Lỗi cơ sở dữ liệu khi xóa đánh giá."

    @staticmethod
    def update_review(review_id, user_id, rating=None, comment=None):
        """Cập nhật đánh giá, kiểm tra quyền sở hữu."""
        review = Review.query.get(review_id)
        if not review:
            return None, "Không tìm thấy đánh giá."

        # KIỂM TRA QUYỀN: Chỉ người tạo mới được sửa
        if review.reviewer_id != user_id:
            return None, "Bạn không có quyền sửa đánh giá này."

        updated = False
        try:
            if rating is not None:
                try:
                    rating_int = int(rating)
                    # Model validator sẽ kiểm tra 0-5, nhưng có thể check lại ở đây
                    if not (0 <= rating_int <= 5): raise ValueError()
                    review.rating = rating_int
                    updated = True
                except (ValueError, TypeError):
                     raise ValueError("Rating phải là một số nguyên từ 0 đến 5.") # Ném lỗi ra ngoài

            if comment is not None: # Cho phép cập nhật comment thành chuỗi rỗng
                review.comment = comment
                updated = True

            if updated:
                db.session.commit()
                return review, None # Trả về review và không có lỗi
            else:
                 return review, "Không có thông tin nào được cập nhật."

        except ValueError as ve: # Lỗi validation rating
             return None, str(ve)
        except Exception as e:
             db.session.rollback()
             logger.error(f"Lỗi DB khi cập nhật review {review_id}: {e}", exc_info=True)
             return None, "Lỗi cơ sở dữ liệu khi cập nhật đánh giá."