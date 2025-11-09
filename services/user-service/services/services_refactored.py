import os
import secrets
import smtplib
import string
from email.mime.text import MIMEText

from app import db, r
from models.profile import Profile
from models.user import User


class ProfileService:
    @staticmethod
    def create_empty_profile(user_id, full_name=None):
        """Tạo một profile rỗng cho user_id. Trả về (profile, None) nếu thành công."""
        if Profile.query.filter_by(user_id=user_id).first():
            return None, "Profile already exists"
        
        new_profile = Profile(user_id=user_id, full_name=full_name)
        db.session.add(new_profile)
        return new_profile, None

    @staticmethod
    def get_profile_by_user_id(user_id):
        return Profile.query.filter_by(user_id=user_id).first()
    
    @staticmethod
    def update_profile(user_id, new_data):
        profile = ProfileService.get_profile_by_user_id(user_id)
        if not profile:
            return None, "Profile not found"

        if 'full_name' in new_data: profile.full_name = new_data['full_name']
        if 'phone_number' in new_data: profile.phone_number = new_data['phone_number']
        if 'bank_name' in new_data: profile.bank_name = new_data['bank_name']
        if 'account_number' in new_data: profile.account_number= new_data['account_number']
        if 'address' in new_data: profile.address = new_data['address']
        if 'bio' in new_data: profile.bio = new_data['bio']
        
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

    @staticmethod
    def delete_profile_by_user_id(user_id):
        """Xóa profile khi user bị xóa."""
        profile = Profile.query.filter_by(user_id=user_id).first()
        if profile:
            db.session.delete(profile) 
        return True

class UserService:
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    APP_PASSWORD = os.getenv("APP_PASSWORD")

    @staticmethod
    def create_user(email, username, password, role="member", status="active"):
        if User.query.filter_by(email=email).first():
            return None, "Email already exists"
        if User.query.filter_by(username=username).first():
            return None, "Username already exists"
            
        user = User(username=username, email=email, role=role, status=status)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
 
        profile, error = ProfileService.create_empty_profile(user.user_id, user.username)
        if error:
            db.session.rollback()
            return None, error 
            
        db.session.commit()
        return user, None

    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)

    @staticmethod
    def get_all_users():
        return User.query.all()

    @staticmethod
    def get_user_by_email_or_username(email_username):
        user = User.query.filter_by(email=email_username).first()
        if not user:
            user = User.query.filter_by(username=email_username).first()
        return user

    @staticmethod
    def update_user_by_member(user_id, data):
        user = UserService.get_user_by_id(user_id)
        if not user:
            return None, "User not found"
        
        if 'username' in data and data['username']:
            # Kiểm tra username mới có tồn tại chưa
            existing_user = User.query.filter(User.username == data['username'], User.user_id != user_id).first()
            if existing_user:
                return None, "New username already exists"
            user.username = data['username']
        
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        db.session.commit()
        return user, None

    @staticmethod
    def delete_user(user_id):
        user = UserService.get_user_by_id(user_id)
        if not user:
            return False, "User not found"
         
        ProfileService.delete_profile_by_user_id(user_id)
        
        db.session.delete(user)
        db.session.commit()
        return True, "User deleted successfully"

    @staticmethod
    def toggle_user_lock(user_id):
        user = UserService.get_user_by_id(user_id)
        if not user:
            return None, "User not found"
        
        if user.status == "active":
            user.status = "locked"
        else:
            user.status = "active"
        
        db.session.commit()
        return user, None
        
    @staticmethod
    def update_user_by_admin(user_id, data):
        user = UserService.get_user_by_id(user_id)
        if not user:
            return None, "User not found"
        
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'password' in data and data['password']:
             user.set_password(data['password'])
        if 'role' in data:
            user.role = data['role']
        if 'status' in data:
            user.status = data['status']
            
        db.session.commit()
        return user, None

    @staticmethod
    def send_reset_otp(email):
        user = User.query.filter_by(email=email).first()
        if not user:
            return False, "Email does not exist"
        
        otp = ''.join(secrets.choice(string.digits) for _ in range(6)) 
        r.setex(f"otp:{email}", 300, otp)
        
        try:
            subject = "Your OTP Code"
            body = f"Your OTP code is: {otp}. It will expire in 5 minutes."
            msg = MIMEText(body, "plain", "utf-8")
            msg["Subject"] = subject
            msg["From"] = UserService.SENDER_EMAIL
            msg["To"] = email
            
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(UserService.SENDER_EMAIL, UserService.APP_PASSWORD)
                server.sendmail(UserService.SENDER_EMAIL, email, msg.as_string())
            
            return True, "OTP has been sent to your email."
        except Exception as e: 
            print(f"ERROR sending email: {e}")
            return False, "Failed to send OTP email."

    @staticmethod
    def verify_otp_and_reset_password(email, input_otp, new_password): 
        saved_otp = r.get(f"otp:{email}")
        if not saved_otp or input_otp != saved_otp:
            return False, "Invalid or expired OTP."
            
        user = User.query.filter_by(email=email).first()
        if not user: 
            return False, "User not found."
             
        user.set_password(new_password)
        db.session.commit() 
        r.delete(f"otp:{email}")
        
        return True, "Password has been reset successfully."