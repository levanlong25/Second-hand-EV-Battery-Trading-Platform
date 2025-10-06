from models.profile import Profile
from app import db

class ProfileService:
    @staticmethod
    def create_empty_profile(user_id): 
        if Profile.query.filter_by(user_id=user_id).first():
            return {"message": "Profile already exists for this user"}            
        new_profile = Profile(
            user_id=user_id,
            full_name=None,
            phone_number=None,
            avatar_url=None,
            address=None,
            bio=None
        )
        db.session.add(new_profile) 
        return new_profile
    @staticmethod
    def get_profile_by_user_id(user_id):
        return Profile.query.filter_by(user_id = user_id).first()
    @staticmethod
    def update_profile(user_id, new_full_name=None, new_phone_number=None, new_address=None, new_bio=None): 
        profile = ProfileService.get_profile_by_user_id(user_id)        
        if not profile:
            return {"error": "Profile not found"}
        if new_full_name is not None and new_full_name.strip() != "":
            profile.full_name = new_full_name
        if new_phone_number is not None and new_phone_number.strip() != "":
            profile.phone_number = new_phone_number
        if new_address is not None and new_address.strip() != "":
            profile.address = new_address
        if new_bio is not None and new_bio.strip() != "":
            profile.bio = new_bio           
        db.session.commit()
        return {"message": "Profile updated successfully"}
    @staticmethod
    def update_avatar(user_id, new_avatar):
        profile = ProfileService.get_profile_by_user_id(user_id)        
        if not profile:
            return {"error": "Profile not found"}
        profile.avatar_url = new_avatar
        db.session.commit()
        return {"message": "Avatar updated successfully"}
