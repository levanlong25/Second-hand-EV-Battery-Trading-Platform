from models.review import Review
from app import db

class ReviewService:
    @staticmethod
    def create_review(transaction_id, reviewer_id, reviewed_user_id, rating, comment=None):
        review = Review(
            transaction_id=transaction_id,
            reviewer_id=reviewer_id,
            reviewed_user_id=reviewed_user_id,
            rating=rating,
            comment=comment
        )
        db.session.add(review)
        db.session.commit()
        return review

    @staticmethod
    def get_reviews_by_transaction(transaction_id):
        return Review.query.filter_by(transaction_id=transaction_id).all()
    @staticmethod
    def get_reviews_by_user(user_id):
        return Review.query.filter_by(reviewed_user_id=user_id).all()

    @staticmethod
    def delete_review(review_id):
        review = Review.query.get(review_id)
        if not review:
            return {"error": "Review not found"}
        db.session.delete(review)
        db.session.commit()
        return {"message": "Review deleted successfully"}

    @staticmethod
    def update_review(review_id, rating=None, comment=None):
        review = Review.query.get(review_id)
        if not review:
            return {"error": "Review not found"}
        if rating is not None:
            review.rating = rating
        if comment is not None:
            review.comment = comment
        db.session.commit()
        return review