from functools import wraps
from flask import Blueprint, jsonify, request, current_app
import os 
from services.services_refactored import UserService as UserLogic
from services.services_refactored import ProfileService as ProfileLogic 
from controllers.controllers_api import serialize_user, serialize_profile  
import logging

internal_bp = Blueprint('internal_api', __name__, url_prefix='/internal')  
logger = logging.getLogger(__name__)  
 
def internal_api_key_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            provided_key = request.headers.get('X-Internal-Api-Key') 
            correct_key = os.environ.get('INTERNAL_API_KEY')  

            if not correct_key:
                 logger.error("INTERNAL_API_KEY chưa được cấu hình!")
                 return jsonify(error="Lỗi cấu hình server"), 500

            if provided_key and provided_key == correct_key:
                return fn(*args, **kwargs)
            else:
                logger.warning(f"Từ chối truy cập internal API: Sai API Key. Header: {request.headers.get('X-Internal-Api-Key')}")
                return jsonify(error="Unauthorized internal access"), 403
        return decorator
    return wrapper

# --- Các Endpoint Nội Bộ ---

@internal_bp.route("/users", methods=["GET"])
@internal_api_key_required()
def internal_get_all_users():
    """Admin service gọi để lấy tất cả user (có lọc)."""
    status = request.args.get('status')
    
    # Giả định UserLogic.get_all_users() trả về 1 list các object User
    # Lọc được thực hiện tại đây
    users = UserLogic.get_all_users() 
    
    if status:
        try:
            # Lọc trong Python
            users = [u for u in users if u.status == status]
        except AttributeError:
            logger.error("Đối tượng User không có thuộc tính 'status' để lọc.")
            # Có thể bỏ qua lỗi và trả về list đầy đủ
            pass
            
    return jsonify([serialize_user(u) for u in users]), 200



@internal_bp.route("/users/<int:user_id>", methods=["GET"])
@internal_api_key_required()
def internal_get_user_details(user_id):
    """Admin service gọi để lấy chi tiết user + profile."""
    user = UserLogic.get_user_by_id(user_id)
    if not user: return jsonify(error="User not found"), 404
    profile = ProfileLogic.get_profile_by_user_id(user_id)  
    return jsonify({
        "user": serialize_user(user),
        "profile": serialize_profile(profile) if profile else None  
    }), 200

@internal_bp.route("/users", methods=["POST"])
@internal_api_key_required()
def internal_create_user():
    """Admin service gọi để tạo user mới."""
    data = request.get_json()
    if not data or not all(k in data for k in ["email", "username", "password"]):
        return jsonify(error="Missing required fields"), 400 
    user, error = UserLogic.create_user(
        email=data["email"],
        username=data["username"],
        password=data["password"],
        role=data.get("role", "member"),
        status=data.get("status", "active")
    )
    if error: return jsonify(error=error), 409
    return jsonify(user=serialize_user(user)), 201  

@internal_bp.route("/users/<int:user_id>/toggle-lock", methods=["POST"])
@internal_api_key_required()
def internal_toggle_user_lock(user_id):
    """Admin service gọi để khóa/mở khóa user.""" 
    user, error = UserLogic.toggle_user_lock(user_id)
    if error: return jsonify(error=error), 404
    return jsonify(user=serialize_user(user)), 200

@internal_bp.route("/users/<int:user_id>", methods=["PUT"])
@internal_api_key_required()
def internal_update_user(user_id):
    """Admin service gọi để cập nhật thông tin user."""
    data = request.get_json()
    if not data: return jsonify(error="Missing JSON body"), 400 
    user, error = UserLogic.update_user_by_admin(user_id, data)
    if error: return jsonify(error=error), 404
    return jsonify(user=serialize_user(user)), 200

@internal_bp.route("/users/<int:user_id>", methods=["DELETE"])
@internal_api_key_required()
def internal_delete_user(user_id):
    """Admin service gọi để xóa user.""" 
    success, message = UserLogic.delete_user(user_id)
    if not success: return jsonify(error=message), 404
    return jsonify(message=message), 200 