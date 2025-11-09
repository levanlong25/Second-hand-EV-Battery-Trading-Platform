from functools import wraps

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (create_access_token, get_jwt, get_jwt_identity,
                                jwt_required, verify_jwt_in_request)
 
from app import jwt  
from services.services_refactored import ProfileService as ProfileLogic
from services.services_refactored import UserService as UserLogic

# Tạo Blueprint cho tất cả các API endpoint, với tiền tố /api
api_bp = Blueprint('api', __name__, url_prefix='/api')

# --- Helper Functions ---
def serialize_user(user):
    """Chuyển đổi đối tượng User thành dictionary, ẩn mật khẩu."""
    if not user: return None
    return {
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "status": user.status
    }
def serialize_info(user):
    if not user: return None
    return {
        "user_id": user.user_id,
        "username": user.username
    }
def serialize_bank(profile):
    if not profile: return None
    return {
        "bank_name": profile.bank_name,
        "account_number": profile.account_number,
    }
def serialize_profile(profile):
    """Chuyển đổi đối tượng Profile thành dictionary."""
    if not profile: return None
    return {
        "user_id": profile.user_id,
        "full_name": profile.full_name,
        "phone_number": profile.phone_number,
        "bank_name": profile.bank_name,
        "account_number": profile.account_number,
        "address": profile.address,
        "bio": profile.bio
    }

# --- Custom Decorator for Admin Role ---
def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") == "admin":
                return fn(*args, **kwargs)
            else:
                return jsonify(error="Admins only!"), 403
        return decorator
    return wrapper

# --- JWT Configuration Callbacks ---
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    """
    Hàm này được gọi mỗi khi một endpoint được bảo vệ được truy cập,
    và nó sẽ trả về đối tượng User dựa trên identity trong token.
    """
    identity = jwt_data["sub"]
    return UserLogic.get_user_by_id(identity)

@jwt.additional_claims_loader
def add_claims_to_access_token(identity):
    """
    Hàm này được gọi khi tạo token. Nó nhận vào identity (user_id),
    tìm user trong DB và thêm 'role' vào trong token.
    """
    user = UserLogic.get_user_by_id(identity)
    if user:
        return {"role": user.role}
    return {}

# --- Authentication & Password Reset Endpoints ---

@api_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data or not all(k in data for k in ["email", "username", "password"]):
        return jsonify({"error": "Missing required fields: email, username, password"}), 400
    
    user, error = UserLogic.create_user(data["email"], data["username"], data["password"])
    if error:
        return jsonify({"error": error}), 409
    
    return jsonify({
        "message": "Registration successful!",
        "user": serialize_user(user)
    }), 201

@api_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()   
        if not data or not data.get("email_username") or not data.get("password"):
            return jsonify({"error": "Missing email/username or password"}), 400

        user = UserLogic.get_user_by_email_or_username(data["email_username"])
        if not user or not user.check_password(data["password"]):
            return jsonify({"error": "Invalid credentials"}), 401

        if user.status != "active":
            return jsonify({"error": "Account has been locked"}), 403

        access_token = create_access_token(identity=str(user.user_id))
        return jsonify(access_token=access_token)
    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {e}"}), 500

    
@api_bp.route("/send-otp", methods=["POST"])
def send_otp():
    email = request.json.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400
    
    success, message = UserLogic.send_reset_otp(email)
    if not success:
        return jsonify(error=message), 404
    return jsonify(message=message), 200

@api_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    if not data or not all(k in data for k in ["email", "otp", "new_password"]):
        return jsonify({"error": "Missing required fields: email, otp, new_password"}), 400
    
    success, message = UserLogic.verify_otp_and_reset_password(data["email"], data["otp"], data["new_password"])
    if not success:
        return jsonify(error=message), 400
    return jsonify(message=message), 200

# --- Member Account & Profile Endpoints (Protected) ---

@api_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_my_profile():
    current_user_id = get_jwt_identity()
    profile = ProfileLogic.get_profile_by_user_id(current_user_id)
    if not profile:
        return jsonify({"error": "Profile not found"}), 404
    return jsonify(serialize_profile(profile)), 200

@api_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_my_profile():
    current_user_id = get_jwt_identity()
    profile, error = ProfileLogic.update_profile(current_user_id, request.json)
    if error:
        return jsonify({"error": error}), 404
    return jsonify({"message": "Profile updated", "profile": serialize_profile(profile)}), 200

@api_bp.route("/account", methods=["PUT"])
@jwt_required()
def update_my_account():
    current_user_id = get_jwt_identity()
    user, error = UserLogic.update_user_by_member(current_user_id, request.json)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"message": "Account updated successfully", "user": serialize_user(user)}), 200
    
@api_bp.route("/account", methods=["DELETE"])
@jwt_required()
def delete_my_account():
    current_user_id = get_jwt_identity()
    success, message = UserLogic.delete_user(current_user_id)
    if not success:
        return jsonify({"error": message}), 404
    return jsonify({"message": message}), 200

@api_bp.route("/info/<int:user_id>", methods = ['GET'])
def get_info_user(user_id):
    user = UserLogic.get_user_by_id(user_id=user_id)
    return jsonify([serialize_info(user)]), 200

@api_bp.route("/profile/<int:user_id>", methods=["GET"]) 
def get_user_profile(user_id):
    """
    Lấy thông tin profile công khai của một user bất kỳ.
    """
    profile = ProfileLogic.get_profile_by_user_id(user_id)
    
    if not profile: 
        return jsonify({"error": "Không tìm thấy hồ sơ người dùng."}), 404 
    return jsonify(serialize_profile(profile)), 200