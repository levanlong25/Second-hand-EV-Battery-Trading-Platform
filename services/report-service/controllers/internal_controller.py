# report-service/controllers/internal_controller.py
from functools import wraps
from flask import Blueprint, jsonify, request, current_app
import os
import logging
from services.report_service import ReportService
# Import hàm serialize từ controller chính của bạn
from .report_controller import serialize_report 

internal_bp = Blueprint('internal_api', __name__, url_prefix='/internal')
logger = logging.getLogger(__name__)

# --- Decorator Kiểm Tra API Key Nội Bộ (Copy từ service khác) ---
def internal_api_key_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            provided_key = request.headers.get('X-Internal-Api-Key')
            # Đọc key từ biến môi trường (phải được load bởi app.py)
            correct_key = os.environ.get('INTERNAL_API_KEY') 
            if not correct_key:
                 logger.error("INTERNAL_API_KEY chưa được cấu hình!")
                 return jsonify(error="Lỗi cấu hình server"), 500
            if provided_key and provided_key == correct_key:
                return fn(*args, **kwargs)
            else:
                logger.warning(f"Từ chối truy cập internal API (Report): Sai API Key.")
                return jsonify(error="Unauthorized internal access"), 403
        return decorator
    return wrapper

# === API NỘI BỘ CHO ADMIN SERVICE GỌI ===

@internal_bp.route("/reports", methods=["GET"])
@internal_api_key_required()
def internal_get_all_reports():
    """Lấy tất cả báo cáo, có thể lọc theo status."""
    status_filter = request.args.get('status')
    try:
        reports = ReportService.get_all_reports(status_filter=status_filter)
        # (Lưu ý: serialize_report này chưa có username)
        return jsonify([serialize_report(r) for r in reports]), 200
    except Exception as e:
        logger.error(f"Lỗi internal_get_all_reports: {e}", exc_info=True)
        return jsonify(error="Lỗi máy chủ nội bộ."), 500

@internal_bp.route("/reports/<int:report_id>/status", methods=["PUT"])
@internal_api_key_required()
def internal_update_report_status(report_id):
    """Cập nhật trạng thái (resolved/dismissed) cho một báo cáo."""
    data = request.get_json()
    new_status = data.get('status')
    if not new_status:
        return jsonify(error="Thiếu 'status' trong body"), 400

    try:
        report, message = ReportService.update_report_status(report_id, new_status)
        if not report:
            return jsonify(error=message), 404 # Hoặc 400
        return jsonify(message=message, report=serialize_report(report)), 200
    except Exception as e:
        logger.error(f"Lỗi internal_update_report_status {report_id}: {e}", exc_info=True)
        return jsonify(error="Lỗi máy chủ nội bộ."), 500

@internal_bp.route("/reports/by-reporter/<int:user_id>", methods=["GET"])
@internal_api_key_required()
def internal_get_reports_by_reporter(user_id):
    """API nội bộ để lấy các report do một user viết."""
    try:
        reports = ReportService.get_reports_by_reporter(user_id)
        return jsonify([serialize_report(r) for r in reports]), 200
    except Exception as e:
         logger.error(f"Lỗi internal_get_reports_by_reporter cho user {user_id}: {e}", exc_info=True)
         return jsonify(error="Lỗi máy chủ nội bộ."), 500
