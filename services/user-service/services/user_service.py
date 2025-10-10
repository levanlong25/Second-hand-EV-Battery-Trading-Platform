from models.user import User
from app import db
import string
import secrets
import smtplib
from email.mime.text import MIMEText
from services.profile_service import ProfileService


class UserService:

    @staticmethod
    def create_user(email, username, password):
        user = User.query.filter_by(email=email).first()
        if user:
            return {"error": "email is exists"}
        user = User.query.filter_by(username=username).first()
        if user:
            return {"error": "username is exists"}
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        profile_result = ProfileService.create_empty_profile(user.user_id)
        if "error" in profile_result:
            db.session.rollback()
            return profile_result
        db.session.commit()
        return user

    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_user_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_all_user():
        users = User.query.all()
        return [
            {
                "user_id": u.user_id,
                "username": u.username,
                "password": u.password,
                "role": u.role,
                "status": u.status
            }
            for u in users
        ]

    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)

    @staticmethod
    def delete_user_by_id(user_id):
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not exists"}
        db.session.delete(user)
        db.session.commit()
        return {"message": "Delete successfully"}

    @staticmethod
    def update_by_member(user_id, new_username=None, new_password=None):
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}
        if new_username != None:
            user.username = new_username
        if new_password != None:
            user.set_password(new_password)
        db.session.commit()
        return {"message": "User updated successfully"}

    @staticmethod
    def find_by_id(user_id):
        user = User.query.get(user_id)
        return {
            "user_id": user.user_id,
            "username": user.username,
            "password": user.password,
            "role": user.role,
            "active": user.active
        }

    @staticmethod
    def find_by_username(username):
        user = User.query.filter_by(username).first()
        return {
            "user_id": user.user_id,
            "username": user.username,
            "password": user.password,
            "role": user.role,
            "active": user.active
        }

    @staticmethod
    def user_lock(user_id):
        user = User.query.get(user_id)
        if user.status == "active":
            user.status = "lock"
        if user.status == "lock":
            user.status = "active"
        db.session.commit()
        return {"message": "change status successfully"}

    @staticmethod
    def register(email, username, password):
        user = UserService.create_user(email, username, password)
        if "error" in user:
            return user["error"]
        return {"message": "Registration successful! Please login."}

    @staticmethod
    def login(email_username, password):
        user = UserService.get_user_by_email(email=email_username)
        if not user:
            user = UserService.get_user_by_username(username=email_username)
        if not user or not user.check_password(password):
            return {"error": "Invalid email or username or password"}
        if user.status != "active":
            return {"error": "Account has been locked. Please contact admin"}
        return user

    @staticmethod
    def create_otp(length=6):
        digit = string.digits
        return ''.join(secrets.choice(digit) for _ in range(length))

    @staticmethod
    def send_otp_via_mail(receive_email, otp):
        sender_email = "lelonh0810@gmail.com"
        app_password = "fyrszjrttsnlybpd"

        subject = "Mã OTP xác thực"
        body = f"Mã OTP của bạn là: {otp}"

        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = receive_email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receive_email, msg.as_string())
        print(f"DEBUG: Sent OTP {otp} to {receive_email}")

    otp_store = {}

    @staticmethod
    def send_reset_otp(receive_email):
        user = UserService.get_user_by_email(receive_email)
        if not user:
            return {"error": {"email not exists"}}
        otp = UserService.create_otp()
        UserService.otp_store[receive_email] = otp
        UserService.send_otp_via_mail(receive_email, otp)
        return {"message": {"Otp sent to email"}}

    @staticmethod
    def forget_password(receive_email, input_otp, new_password):
        user = UserService.get_user_by_email(receive_email)
        if not user:
            return {"error": "Email not exists"}
        saved_otp = UserService.otp_store.get(receive_email)
        if not saved_otp:
            return {"error": "OTP not found, please request again"}
        if input_otp != saved_otp:
            return {"error": "OTP not suitable"}
        user.set_password(new_password)
        db.session.commit()

        del UserService.otp_store[receive_email]
        return {"message": "Password reset successfully"}

    @staticmethod
    def create_user_by_admin(email, username, password, role="member", status="active"):
        if User.query.filter_by(email=email).first():
            return {"error": "email is exists"}
        if User.query.filter_by(username=username).first():
            return {"error": "username is exists"}
        user = User(username=username, email=email, role=role, status=status)
        user.set_password(password)
        db.session.add(user)
        try:
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {e}"}

    @staticmethod
    def update_by_admin(user_id, new_username=None, new_password=None, new_role=None, new_status=None):
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}
        if new_username:
            user.username = new_username
        if new_password:
            user.set_password(new_password)
        if new_role:
            user.role = new_role
        if new_status:
            user.status = new_status
        db.session.commit()
        return {"message": "User updated successfully by admin"}, 200
