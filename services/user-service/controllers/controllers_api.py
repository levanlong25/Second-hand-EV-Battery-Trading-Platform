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

def serialize_profile(profile):
    """Chuyển đổi đối tượng Profile thành dictionary."""
    if not profile: return None
    return {
        "user_id": profile.user_id,
        "full_name": profile.full_name,
        "phone_number": profile.phone_number,
        "address": profile.address,
        "bio": profile.bio,
        "avatar_url": profile.avatar_url
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

# --- Admin Management Endpoints (Admin Protected) ---

# @api_bp.route("/admin/users", methods=["GET"])
# @admin_required()
# def get_all_users():
#     users = UserLogic.get_all_users()
#     return jsonify([serialize_user(u) for u in users]), 200

# @api_bp.route("/admin/users/<int:user_id>", methods=["GET"])
# @admin_required()
# def get_user_details_by_admin(user_id):
#     user = UserLogic.get_user_by_id(user_id)
#     if not user: return jsonify(error="User not found"), 404
#     profile = ProfileLogic.get_profile_by_user_id(user_id)
#     return jsonify({
#         "user": serialize_user(user),
#         "profile": serialize_profile(profile)
#     }), 200

# @api_bp.route("/admin/users", methods=["POST"])
# @admin_required()
# def create_user_by_admin():
#     data = request.get_json()
#     if not data or not all(k in data for k in ["email", "username", "password"]):
#         return jsonify({"error": "Missing required fields"}), 400
    
#     user, error = UserLogic.create_user(
#         email=data["email"],
#         username=data["username"],
#         password=data["password"],
#         role=data.get("role", "member"),
#         status=data.get("status", "active")
#     )
#     if error:
#         return jsonify({"error": error}), 409
#     return jsonify({"message": "User created by admin", "user": serialize_user(user)}), 201

# @api_bp.route("/admin/users/<int:user_id>/toggle-lock", methods=["POST"])
# @admin_required()
# def toggle_user_lock(user_id):
#     current_admin_id = get_jwt_identity()
#     if user_id == current_admin_id:
#         return jsonify(error="Admin cannot lock their own account"), 400

#     user, error = UserLogic.toggle_user_lock(user_id)
#     if error:
#         return jsonify({"error": error}), 404
#     return jsonify({"message": f"User status changed to {user.status}", "user": serialize_user(user)}), 200

# @api_bp.route("/admin/users/<int:user_id>", methods=["PUT"])
# @admin_required()
# def update_user_by_admin(user_id):
#     user, error = UserLogic.update_user_by_admin(user_id, request.json)
#     if error:
#         return jsonify({"error": error}), 404
#     return jsonify({"message": "User updated by admin", "user": serialize_user(user)}), 200

# @api_bp.route("/admin/users/<int:user_id>", methods=["DELETE"])
# @admin_required()
# def delete_user_by_admin(user_id):
#     current_admin_id = get_jwt_identity()
#     if user_id == current_admin_id:
#         return jsonify(error="Admin cannot delete their own account"), 400

#     success, message = UserLogic.delete_user(user_id)
#     if not success:
#         return jsonify({"error": message}), 404
#     return jsonify({"message": message}), 200