# admin-service/controllers/admin_controller.py
from functools import wraps
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity, verify_jwt_in_request
import requests
import os
import logging

admin_bp = Blueprint('admin_api', __name__, url_prefix='/admin')  
logger = logging.getLogger(__name__)

# Đọc URL và Key từ môi trường
USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL')
LISTING_SERVICE_URL = os.environ.get('LISTING_SERVICE_URL')
TRANSACTION_SERVICE_URL = os.environ.get('TRANSACTION_SERVICE_URL')
AUCTION_SERVICE_URL = os.environ.get('AUCTION_SERVICE_URL')
REVIEW_SERVICE_URL = os.environ.get('REVIEW_SERVICE_URL')
REPORT_SERVICE_URL = os.environ.get('REPORT_SERVICE_URL')
PRICING_SERVICE_URL = os.environ.get('PRICING_SERVICE_URL')
INTERNAL_API_KEY = os.environ.get('INTERNAL_API_KEY')
REQUEST_TIMEOUT = 5  

# --- Decorator kiểm tra quyền Admin (Copy từ user-service) ---
def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                if claims.get("role") == "admin":
                    return fn(*args, **kwargs)
                else:
                    return jsonify(error="Admin access required"), 403
            except Exception as e:
                 logger.error(f"Admin auth error: {e}")
                 return jsonify(error="Invalid token or authorization error"), 401
        return decorator
    return wrapper

# --- Hàm helper để gọi User Service nội bộ ---
def call_user_service(method, endpoint, json_data=None):
    """Hàm tiện ích để gọi API nội bộ của User Service."""
    if not USER_SERVICE_URL or not INTERNAL_API_KEY:
        logger.error("USER_SERVICE_URL hoặc INTERNAL_API_KEY chưa được cấu hình!")
        return {"error": "Lỗi cấu hình server nội bộ"}, 500

    url = f"{USER_SERVICE_URL}/internal{endpoint}"  
    headers = {'X-Internal-Api-Key': INTERNAL_API_KEY}

    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, json=json_data, timeout=REQUEST_TIMEOUT)
        elif method.upper() == 'PUT':
            response = requests.put(url, headers=headers, json=json_data, timeout=REQUEST_TIMEOUT)
        elif method.upper() == 'DELETE':
             response = requests.delete(url, headers=headers, timeout=REQUEST_TIMEOUT)
        else:
            return {"error": "Phương thức HTTP không hỗ trợ"}, 500
 
        if 200 <= response.status_code < 300: 
             if response.content:
                 return response.json(), response.status_code
             else: 
                 return {"message": "Thao tác thành công"}, response.status_code
        else: 
            try:
                 error_json = response.json()
                 return {"error": error_json.get("error", response.text)}, response.status_code
            except: 
                 return {"error": f"Lỗi từ User Service ({response.status_code})"}, response.status_code

    except requests.exceptions.RequestException as e:
        logger.error(f"Lỗi kết nối đến User Service ({url}): {e}")
        return {"error": f"Không thể kết nối đến User Service: {e}"}, 503
    
def call_listing_service(method, endpoint, json_data=None):
    """Hàm tiện ích để gọi API nội bộ của Listing Service."""
    if not LISTING_SERVICE_URL or not INTERNAL_API_KEY:
        logger.error("LISTING_SERVICE_URL hoặc INTERNAL_API_KEY chưa được cấu hình!")
        return {"error": "Lỗi cấu hình server nội bộ"}, 500

    url = f"{LISTING_SERVICE_URL}/internal{endpoint}"  
    headers = {'X-Internal-Api-Key': INTERNAL_API_KEY} 
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        elif method.upper() == 'PUT':
            response = requests.put(url, headers=headers, json=json_data, timeout=REQUEST_TIMEOUT)
        elif method.upper() == 'DELETE':
             response = requests.delete(url, headers=headers, timeout=REQUEST_TIMEOUT) 
        else:
            return {"error": "Phương thức HTTP không hỗ trợ"}, 500
 
        if 200 <= response.status_code < 300:
             if response.content: return response.json(), response.status_code
             else: return {"message": "Thao tác thành công"}, response.status_code
        else:
            try: error_json = response.json(); return {"error": error_json.get("error", response.text)}, response.status_code
            except: return {"error": f"Lỗi từ Listing Service ({response.status_code})"}, response.status_code
    except requests.exceptions.RequestException as e:
        logger.error(f"Lỗi kết nối đến Listing Service ({url}): {e}")
        return {"error": f"Không thể kết nối đến Listing Service: {e}"}, 503

def call_auction_service(method, endpoint, json_data=None):
    """Hàm tiện ích để gọi API nội bộ của Auction Service."""
    if not AUCTION_SERVICE_URL or not INTERNAL_API_KEY:
        logger.error("AUCTION_SERVICE_URL hoặc INTERNAL_API_KEY chưa được cấu hình!")
        return {"error": "Lỗi cấu hình server nội bộ"}, 500

    url = f"{AUCTION_SERVICE_URL}/internal{endpoint}" 
    headers = {'X-Internal-Api-Key': INTERNAL_API_KEY} 
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        elif method.upper() == 'POST':
             response = requests.post(url, headers=headers, json=json_data, timeout=REQUEST_TIMEOUT)
        elif method.upper() == 'PUT':
            response = requests.put(url, headers=headers, json=json_data, timeout=REQUEST_TIMEOUT)
        elif method.upper() == 'DELETE':
             response = requests.delete(url, headers=headers, timeout=REQUEST_TIMEOUT)
        else:
            return {"error": "Phương thức HTTP không hỗ trợ"}, 500
 
        if 200 <= response.status_code < 300:
             if response.content: return response.json(), response.status_code
             else: return {"message": "Thao tác thành công"}, response.status_code
        else:
            try: error_json = response.json(); return {"error": error_json.get("error", response.text)}, response.status_code
            except: return {"error": f"Lỗi từ Auction Service ({response.status_code})"}, response.status_code
    except requests.exceptions.RequestException as e:
        logger.error(f"Lỗi kết nối đến Auction Service ({url}): {e}")
        return {"error": f"Không thể kết nối đến Auction Service: {e}"}, 503
    
# --- Hàm helper để gọi Transaction Service ---
def call_transaction_service(method, endpoint, json_data=None):
    """Hàm tiện ích để gọi API nội bộ của Transaction Service."""
    if not TRANSACTION_SERVICE_URL or not INTERNAL_API_KEY:
        logger.error("TRANSACTION_SERVICE_URL hoặc INTERNAL_API_KEY chưa được cấu hình!")
        return {"error": "Lỗi cấu hình server nội bộ"}, 500

    url = f"{TRANSACTION_SERVICE_URL}/internal{endpoint}"  
    headers = {'X-Internal-Api-Key': INTERNAL_API_KEY} 
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        elif method.upper() == 'PUT':
            response = requests.put(url, headers=headers, json=json_data, timeout=REQUEST_TIMEOUT) 
        else:
            return {"error": "Phương thức HTTP không hỗ trợ"}, 500
 
        if 200 <= response.status_code < 300:
             if response.content: return response.json(), response.status_code
             else: return {"message": "Thao tác thành công"}, response.status_code
        else:
            try: error_json = response.json(); return {"error": error_json.get("error", response.text)}, response.status_code
            except: return {"error": f"Lỗi từ Transaction Service ({response.status_code})"}, response.status_code
    except requests.exceptions.RequestException as e:
        logger.error(f"Lỗi kết nối đến Transaction Service ({url}): {e}")
        return {"error": f"Không thể kết nối đến Transaction Service: {e}"}, 503
    
def call_review_service(method, endpoint, json_data=None):
    """Hàm tiện ích để gọi API nội bộ của Review Service."""
    if not REVIEW_SERVICE_URL or not INTERNAL_API_KEY:
        logger.error("REVIEW_SERVICE_URL hoặc INTERNAL_API_KEY chưa được cấu hình!")
        return {"error": "Lỗi cấu hình server nội bộ"}, 500
    
    url = f"{REVIEW_SERVICE_URL}/internal{endpoint}"  
    headers = {'X-Internal-Api-Key': INTERNAL_API_KEY}
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT) 
        else:
            return {"error": "Phương thức HTTP không hỗ trợ"}, 500
 
        if 200 <= response.status_code < 300:
             if response.content: return response.json(), response.status_code
             else: return {"message": "Thao tác thành công"}, response.status_code
        else:
            try: error_json = response.json(); return {"error": error_json.get("error", response.text)}, response.status_code
            except: return {"error": f"Lỗi từ Review Service ({response.status_code})"}, response.status_code
    except requests.exceptions.RequestException as e:
        logger.error(f"Lỗi kết nối đến Review Service ({url}): {e}")
        return {"error": f"Không thể kết nối đến Review Service: {e}"}, 503

def call_report_service(method, endpoint, json_data=None):
    """Hàm tiện ích để gọi API nội bộ của Report Service."""
    if not REPORT_SERVICE_URL or not INTERNAL_API_KEY:
        logger.error("REPORT_SERVICE_URL hoặc INTERNAL_API_KEY chưa được cấu hình!")
        return {"error": "Lỗi cấu hình server nội bộ"}, 500
    
    url = f"{REPORT_SERVICE_URL}/internal{endpoint}"  
    headers = {'X-Internal-Api-Key': INTERNAL_API_KEY}
    
    try:
        response = None
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        elif method.upper() == 'PUT':
            response = requests.put(url, headers=headers, json=json_data, timeout=REQUEST_TIMEOUT)
        elif method.upper() == 'POST':
             response = requests.post(url, headers=headers, json=json_data, timeout=REQUEST_TIMEOUT)
        elif method.upper() == 'DELETE':
             response = requests.delete(url, headers=headers, timeout=REQUEST_TIMEOUT)
        else:
            return {"error": "Phương thức HTTP không hỗ trợ"}, 500
 
        if 200 <= response.status_code < 300:
             if response.content: return response.json(), response.status_code
             else: return {"message": "Thao tác thành công"}, response.status_code
        else:
            try: error_json = response.json(); return {"error": error_json.get("error", response.text)}, response.status_code
            except: return {"error": f"Lỗi từ Report Service ({response.status_code})"}, response.status_code
    except requests.exceptions.RequestException as e:
        logger.error(f"Lỗi kết nối đến Report Service ({url}): {e}")
        return {"error": f"Không thể kết nối đến Report Service: {e}"}, 503
    
def call_ai_pricing_service(method, endpoint, json_data=None):
    """Hàm tiện ích để gọi API nội bộ của AI Pricing Service."""
    if not PRICING_SERVICE_URL or not INTERNAL_API_KEY:
        logger.error("AI_PRICING_SERVICE_URL hoặc INTERNAL_API_KEY chưa được cấu hình!")
        return {"error": "Lỗi cấu hình server nội bộ"}, 500
    
    url = f"{PRICING_SERVICE_URL}/internal/admin{endpoint}" # Dùng prefix /internal/admin
    headers = {'X-Internal-Api-Key': INTERNAL_API_KEY}
    
    try:
        response = None
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        elif method.upper() == 'POST':
             response = requests.post(url, headers=headers, json=json_data, timeout=REQUEST_TIMEOUT)
        elif method.upper() == 'DELETE':
             response = requests.delete(url, headers=headers, timeout=REQUEST_TIMEOUT)
        else:
            return {"error": "Phương thức HTTP không hỗ trợ"}, 500

        # Xử lý response
        if 200 <= response.status_code < 300:
             if response.content: return response.json(), response.status_code
             else: return {"message": "Thao tác thành công"}, response.status_code
        else:
            try: error_json = response.json(); return {"error": error_json.get("error", response.text)}, response.status_code
            except: return {"error": f"Lỗi từ AI Pricing Service ({response.status_code})"}, response.status_code
    except requests.exceptions.RequestException as e:
        logger.error(f"Lỗi kết nối đến AI Pricing Service ({url}): {e}")
        return {"error": f"Không thể kết nối đến AI Pricing Service: {e}"}, 503
# --- Các Endpoint Admin (Gọi User Service) ---

@admin_bp.route("/users", methods=["GET"])
@admin_required()
def get_all_users():
    """Lấy danh sách user từ User Service (có lọc)."""
    status = request.args.get('status')
    endpoint = "/users"
    if status:
        endpoint += f"?status={status}"
        
    data, status_code = call_user_service('GET', endpoint)
    return jsonify(data), status_code


@admin_bp.route("/users/<int:user_id>", methods=["GET"])
@admin_required()
def get_user_details_by_admin(user_id):
    """Lấy chi tiết user + profile từ User Service."""
    data, status_code = call_user_service('GET', f'/users/{user_id}')
    return jsonify(data), status_code

@admin_bp.route("/users", methods=["POST"])
@admin_required()
def create_user_by_admin():
    """Tạo user mới thông qua User Service."""
    req_data = request.get_json()
    if not req_data: return jsonify(error="Missing JSON body"), 400 
    data, status_code = call_user_service('POST', '/users', json_data=req_data) 
    return jsonify(data), status_code

@admin_bp.route("/users/<int:user_id>/toggle-lock", methods=["POST"])
@admin_required()
def toggle_user_lock(user_id):
    """Khóa/mở khóa user qua User Service."""
    current_admin_id = int(get_jwt_identity())  
    if user_id == current_admin_id:
        return jsonify(error="Admin không thể khóa tài khoản của chính mình"), 400

    data, status_code = call_user_service('POST', f'/users/{user_id}/toggle-lock') 
    if status_code == 200 and 'user' in data:
         message = f"Trạng thái User {user_id} đã đổi thành {data['user'].get('status', '?')}"
         return jsonify(message=message, user=data['user']), status_code
    return jsonify(data), status_code


@admin_bp.route("/users/<int:user_id>", methods=["PUT"])
@admin_required()
def update_user_by_admin(user_id):
    """Cập nhật user qua User Service."""
    req_data = request.get_json()
    if not req_data: return jsonify(error="Missing JSON body"), 400
    data, status_code = call_user_service('PUT', f'/users/{user_id}', json_data=req_data)
    if status_code == 200 and 'user' in data:
         return jsonify(message="Cập nhật User thành công", user=data['user']), status_code
    return jsonify(data), status_code

@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@admin_required()
def delete_user_by_admin(user_id):
    """Xóa user qua User Service."""
    current_admin_id = int(get_jwt_identity())  
    if user_id == current_admin_id:
        return jsonify(error="Admin không thể xóa tài khoản của chính mình"), 400

    data, status_code = call_user_service('DELETE', f'/users/{user_id}') 
    return jsonify(data), status_code

@admin_bp.route("/users/<int:user_id>/bank", methods=["GET"])
@admin_required()
def get_user_bank_info(user_id):
    """(Admin) Lấy thông tin ngân hàng của user từ User Service.""" 
    data, status_code = call_user_service('GET', f'/users/{user_id}/bank')
    return jsonify(data), status_code

# === CÁC ROUTE ADMIN CHO LISTING ===

@admin_bp.route("/listings", methods=["GET"])
@admin_required()
def get_all_listings():
    """Lấy tất cả listing từ Listing Service (có lọc)."""
    status = request.args.get('status')
    listing_type = request.args.get('type')
    
    params = {}
    if status:
        params['status'] = status
    if listing_type:
        params['type'] = listing_type

    # Cần 1 hàm helper mới để build query string
    query_string = "&".join(f"{key}={value}" for key, value in params.items())
    endpoint = f"/listings"
    if query_string:
        endpoint += f"?{query_string}"

    data, status_code = call_listing_service('GET', endpoint)
    return jsonify(data), status_code


@admin_bp.route("/listings/pending", methods=["GET"])
@admin_required()
def get_pending_listings():
    """Lấy listing chờ duyệt từ Listing Service."""
    data, status_code = call_listing_service('GET', '/listings/pending')
    return jsonify(data), status_code

@admin_bp.route("/listings/<int:listing_id>/status", methods=["PUT"])
@admin_required()
def update_listing_status(listing_id):
    """Duyệt/từ chối listing qua Listing Service."""
    req_data = request.get_json()
    if not req_data or 'status' not in req_data:
        return jsonify(error="Thiếu 'status' trong body"), 400 
    data, status_code = call_listing_service('PUT', f'/listings/{listing_id}/status', json_data=req_data) 
    return jsonify(data), status_code

@admin_bp.route("/listings/<int:listing_id>", methods=["DELETE"])
@admin_required()
def delete_listing_by_admin(listing_id):
    """Xóa listing qua Listing Service.""" 
    data, status_code = call_listing_service('DELETE', f'/listings/{listing_id}')  
    return jsonify(data), status_code

# === THÊM CÁC ROUTE ADMIN CHO TRANSACTION/PAYMENT ===

@admin_bp.route("/payments", methods=["GET"])
@admin_required()
def get_all_payments():
    """Lấy tất cả payment từ Transaction Service (có lọc)."""
    status = request.args.get('status')
    endpoint = "/payments"
    if status:
        endpoint += f"?status={status}"

    data, status_code = call_transaction_service('GET', endpoint)
    return jsonify(data), status_code



@admin_bp.route("/payments/<int:payment_id>/approve", methods=["PUT"])
@admin_required()
def approve_payment(payment_id):
    """Duyệt payment qua Transaction Service."""
    data, status_code = call_transaction_service('PUT', f'/payments/{payment_id}/approve')
    return jsonify(data), status_code

# === THÊM CÁC ROUTE ADMIN CHO AUCTION ===

@admin_bp.route("/auctions", methods=["GET"])
@admin_required()
def get_all_auctions():
    """Lấy tất cả auction từ Auction Service (có lọc)."""
    status = request.args.get('status')
    auction_type = request.args.get('type')
    
    params = {}
    if status:
        params['status'] = status
    if auction_type:
        params['type'] = auction_type

    query_string = "&".join(f"{key}={value}" for key, value in params.items())
    endpoint = f"/auctions"
    if query_string:
        endpoint += f"?{query_string}"

    data, status_code = call_auction_service('GET', endpoint)
    return jsonify(data), status_code

@admin_bp.route("/auctions/pending", methods=["GET"])
@admin_required()
def get_pending_auctions():
    """Lấy auction chờ duyệt từ Auction Service."""
    data, status_code = call_auction_service('GET', '/auctions/pending')
    return jsonify(data), status_code

@admin_bp.route("/auctions/<int:auction_id>/finalize", methods=["PUT"])
@admin_required()
def finalize_auction(auction_id):
    """Kết thúc auction thủ công qua Auction Service."""
    data, status_code = call_auction_service('PUT', f'/auctions/{auction_id}/finalize')
    return jsonify(data), status_code

@admin_bp.route("/auctions/review", methods=["POST"])
@admin_required()
def review_auction():
    """Duyệt/từ chối auction qua Auction Service."""
    req_data = request.get_json()
    if not req_data or 'auction_id' not in req_data or req_data.get('approve') is None:
        return jsonify(error="Thiếu auction_id hoặc approve"), 400
    data, status_code = call_auction_service('POST', '/auctions/review', json_data=req_data)
    return jsonify(data), status_code

@admin_bp.route("/auctions/<int:auction_id>/status", methods=["PUT"])
@admin_required()
def update_auction_status(auction_id):
    """Cập nhật status auction qua Auction Service."""
    req_data = request.get_json()
    if not req_data or 'auction_status' not in req_data:  
        return jsonify(error="Thiếu 'auction_status'"), 400
    data, status_code = call_auction_service('PUT', f'/auctions/{auction_id}/status', json_data=req_data)
    return jsonify(data), status_code

@admin_bp.route("/auctions/<int:auction_id>", methods=["DELETE"])
@admin_required()
def delete_auction_by_admin(auction_id):
    """Xóa auction qua Auction Service."""
    data, status_code = call_auction_service('DELETE', f'/auctions/{auction_id}')
    return jsonify(data), status_code

# === REVIEW/REPORT ===
        
@admin_bp.route("/reviews/by-user/<int:user_id>", methods=["GET"])
@admin_required()
def get_reviews_by_user(user_id):
    """(Admin) Lấy các đánh giá ĐÃ VIẾT bởi một user.""" 
    data, status_code = call_review_service('GET', f'/reviews/by-reviewer/{user_id}')
    return jsonify(data), status_code

@admin_bp.route("/reports/by-user/<int:user_id>", methods=["GET"])
@admin_required()
def get_reports_by_user(user_id):
    """(Admin) Lấy các báo cáo ĐÃ GỬI bởi một user.""" 
    data, status_code = call_report_service('GET', f'/reports/by-reporter/{user_id}')
    return jsonify(data), status_code

@admin_bp.route("/reports", methods=["GET"])
@admin_required()
def get_all_reports():
    """(Admin) Lấy tất cả báo cáo (có thể lọc theo status)."""
    status_filter = request.args.get('status')
    endpoint = "/reports"
    if status_filter:
        endpoint += f"?status={status_filter}"
    data, status_code = call_report_service('GET', endpoint)
    return jsonify(data), status_code

@admin_bp.route("/reports/<int:report_id>/status", methods=["PUT"])
@admin_required()
def update_report_status(report_id):
    """(Admin) Cập nhật trạng thái báo cáo (resolved/dismissed)."""
    req_data = request.get_json()
    new_status = req_data.get('status')
    if not new_status:
        return jsonify(error="Thiếu 'status' trong body"), 400
     
    if new_status not in ['resolved', 'dismissed']:
         return jsonify(error="Trạng thái không hợp lệ. Chỉ chấp nhận 'resolved' hoặc 'dismissed'."), 400

    data, status_code = call_report_service('PUT', f'/reports/{report_id}/status', json_data=req_data)
    return jsonify(data), status_code

@admin_bp.route("/stats/kpis", methods=["GET"])
@admin_required()
def get_kpi_statistics():
    """(Admin) Lấy các chỉ số KPI từ Transaction Service."""
    data, status_code = call_transaction_service('GET', '/stats/kpis')
    return jsonify(data), status_code


@admin_bp.route("/stats/revenue-trend", methods=["GET"])
@admin_required()
def get_revenue_trend():
    """(Admin) Lấy xu hướng doanh thu từ Transaction Service."""
    data, status_code = call_transaction_service('GET', '/stats/revenue-trend')
    return jsonify(data), status_code

@admin_bp.route("/fees", methods=["GET"])
@admin_required()
def get_fee_config(): 
# Gọi internal API của transaction-service
    data, status_code = call_transaction_service('GET', '/fees')
    return jsonify(data), status_code

@admin_bp.route("/fees", methods=["PUT"])
@admin_required()
def update_fee_config(): 
    req_data = request.get_json()
    if not req_data:
        return jsonify(error="Thiếu JSON body"), 400

    # Truyền thẳng request data (chứa listing_fee_rate, auction_fee_rate)
    data, status_code = call_transaction_service('PUT', '/fees', json_data=req_data)
    return jsonify(data), status_code

@admin_bp.route("/pricing-data", methods=["GET"])
@admin_required()
def get_pricing_data():
    """(Admin) Lấy tất cả dữ liệu giá mẫu từ AI Pricing Service."""
    data, status_code = call_ai_pricing_service('GET', '/sales-data')
    return jsonify(data), status_code

@admin_bp.route("/pricing-data", methods=["POST"])
@admin_required()
def add_pricing_data():
    """(Admin) Thêm dữ liệu giá mẫu mới vào AI Pricing Service."""
    req_data = request.get_json()
    if not req_data:
        return jsonify(error="Thiếu JSON body"), 400
    data, status_code = call_ai_pricing_service('POST', '/sales-data', json_data=req_data)
    return jsonify(data), status_code

@admin_bp.route("/pricing-data/<string:item_type>/<int:item_id>", methods=["DELETE"])
@admin_required()
def delete_pricing_data(item_type, item_id):
    """(Admin) Xóa dữ liệu giá mẫu khỏi AI Pricing Service."""
    if item_type not in ['vehicle', 'battery']:
        return jsonify(error="Loại item không hợp lệ."), 400
    data, status_code = call_ai_pricing_service('DELETE', f'/sales-data/{item_type}/{item_id}')
    return jsonify(data), status_code
