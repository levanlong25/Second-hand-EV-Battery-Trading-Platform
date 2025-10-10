from app import db, r  # Giả sử bạn đã khởi tạo db (SQLAlchemy) và r (Redis) trong app.py
from models.profile import Profile
from models.user import User


class ProfileService:
    @staticmethod
    def create_empty_profile(user_id, full_name=None):
        if Profile.query.filter_by(user_id=user_id).first():
            # Trả về (None, error_message)
            return None, "Profile already exists for this user"
        
        new_profile = Profile(
            user_id=user_id,
            full_name=full_name, # Có thể lấy tên ban đầu từ username
        )
        db.session.add(new_profile)
        # Trả về (result, None)
        return new_profile, None

    @staticmethod
    def get_profile_by_user_id(user_id):
        return Profile.query.filter_by(user_id=user_id).first()

    @staticmethod
    def update_profile(user_id, new_data):
        profile = ProfileService.get_profile_by_user_id(user_id)
        if not profile:
            return None, "Profile not found"

        # Cập nhật các trường nếu chúng tồn tại trong new_data
        if 'full_name' in new_data:
            profile.full_name = new_data['full_name']
        if 'phone_number' in new_data:
            profile.phone_number = new_data['phone_number']
        if 'address' in new_data:
            profile.address = new_data['address']
        if 'bio' in new_data:
            profile.bio = new_data['bio']
        
        db.session.commit()
        return profile, None
        
    @staticmethod
    def update_avatar(user_id, avatar_url):
        profile = ProfileService.get_profile_by_user_id(user_id)
        if not profile:
            return None, "Profile not found"
        profile.avatar_url = avatar_url
        db.session.commit()
        return profile, None