from flask import Blueprint, jsonify, request
from functools import wraps
import os
import logging
from services.pricing_service import PricingService  

internal_admin_bp = Blueprint('internal_admin_api', __name__, url_prefix='/internal/admin')
logger = logging.getLogger(__name__)
pricing_service = PricingService()  
 
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
                logger.warning(f"Từ chối truy cập internal API (Pricing): Sai API Key.")
                return jsonify(error="Unauthorized internal access"), 403
        return decorator
    return wrapper

# --- API cho Admin Service quản lý dữ liệu giá ---

@internal_admin_bp.route("/sales-data", methods=["GET"])
@internal_api_key_required()
def internal_get_sales_data():
    """Lấy tất cả dữ liệu (vehicles và batteries) cho admin."""
    vehicles, batteries, error = pricing_service.get_all_sales_data()
    if error:
        return jsonify(error=error), 500 
    return jsonify(data=vehicles + batteries), 200

@internal_admin_bp.route("/sales-data", methods=["POST"])
@internal_api_key_required()
def internal_add_sale_data():
    """Thêm một bản ghi dữ liệu mới."""
    data = request.get_json()
    if not data or 'type' not in data:
        return jsonify(error="Thiếu 'type' (vehicle/battery) trong body."), 400
        
    new_data, error = pricing_service.add_sale_data(data)
    if error:
        return jsonify(error=error), 400
    return jsonify(message="Thêm dữ liệu thành công.", item=new_data), 201

@internal_admin_bp.route("/sales-data/<string:item_type>/<int:item_id>", methods=["DELETE"])
@internal_api_key_required()
def internal_delete_sale_data(item_type, item_id):
    """Xóa một bản ghi dữ liệu."""
    success, message = pricing_service.delete_sale_data(item_type, item_id)
    if not success:
        status_code = 404 if "Không tìm thấy" in message else 500
        return jsonify(error=message), status_code
    return jsonify(message=message), 200