from flask import Blueprint, request, jsonify, flash, redirect, render_template, url_for, session
from services.review_service import ReviewService, session

USER_SERVICE_URL = "http://user-service:5000"
TRANSACTION_SERVICE_URL = "http://transaction-service:5000"

review_site = Blueprint('review_site', __name__)

login_url = f"{USER_SERVICE_URL}/login"
class ReviewController:
    @review_site.route('/reviews', methods=['POST'])
    def create_review():
        user_id = session.get('user_id')
        if not user_id:
            flash("Vui lòng đăng nhập để gửi đánh giá.")
            return redirect(login_url)
        transaction_id = request.form.get('transaction_id')
        reviewer_id = user_id
        reviewed_user_id = request.form.get('reviewed_user_id')
        rating = request.form.get('rating')
        comment = request.form.get('comment')
        review = ReviewService.create_review(transaction_id, reviewer_id, reviewed_user_id, rating, comment)
        flash("Đánh giá đã được gửi thành công.")
        return redirect()  
    @review_site.route('/update_review/<int:review_id>', methods=['POST'])
    def update_review(review_id):
        user_id = session.get('user_id')
        if not user_id:
            flash("Vui lòng đăng nhập để cập nhật đánh giá.")
            return redirect(login_url)
        review = ReviewService.update_review(review_id)
        if isinstance(review, dict) and "error" in review:
            flash(review["error"])
            return redirect(url_for(''))
        flash("Đánh giá đã được cập nhật thành công.")
        return redirect()
    @review_site.route('/delete_review/<int:review_id>', methods=['POST'])
    def delete_review(review_id):
        user_id = session.get('user_id')
        if not user_id:
            flash("Vui lòng đăng nhập để xóa đánh giá.")
            return redirect(login_url)
        result = ReviewService.delete_review(review_id)
        if "error" in result:
            flash(result["error"])
            return redirect(url_for(''))
        flash("Đánh giá đã được xóa thành công.")
        return redirect()