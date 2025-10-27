# controllers/report_controller.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt # Import get_jwt nếu cần check role
from services.report_service import ReportService # Import service
import logging

logger = logging.getLogger(__name__)

report_api = Blueprint('report_api', __name__, url_prefix='/api')  

# --- Hàm Helper Serialize ---
def serialize_report(report):
    if not report: return None
    return {
        'report_id': report.report_id,
        'reporter_id': report.reporter_id,
        'transaction_id': report.transaction_id,
        'reported_user_id': report.reported_user_id,
        'reason': report.reason,
        'details': report.details,
        'status': report.status,
        'created_at': report.created_at.isoformat() if report.created_at else None
    }

# --- API Endpoints ---

@report_api.route('/reports', methods=['POST'])
@jwt_required()
def create_report_api():
    """Tạo một báo cáo mới."""
    try:
        reporter_id = int(get_jwt_identity())
    except (ValueError, TypeError):
         return jsonify(error="User ID không hợp lệ trong token"), 401

    data = request.get_json()
    if not data: return jsonify(error="Thiếu JSON body"), 400

    transaction_id = data.get('transaction_id')
    reported_user_id = data.get('reported_user_id')
    reason = data.get('reason')
    details = data.get('details')

    if not all([transaction_id, reported_user_id, reason]):
         return jsonify(error="Thiếu các trường bắt buộc: transaction_id, reported_user_id, reason"), 400

    try:
        report, error_message = ReportService.create_report(
            transaction_id=transaction_id,
            reporter_id=reporter_id,
            reported_user_id=reported_user_id,
            reason=reason,
            details=details
        )

        if not report:
            status_code = 409 if "đã báo cáo" in (error_message or "") else 400
            return jsonify(error=error_message or "Không thể tạo báo cáo."), status_code

        return jsonify(report=serialize_report(report)), 201

    except Exception as e:
        logger.error(f"Lỗi khi tạo report: {e}", exc_info=True)
        return jsonify(error="Lỗi máy chủ nội bộ khi tạo báo cáo."), 500


@report_api.route('/reports/<int:report_id>', methods=['DELETE'])
@jwt_required()
def delete_report_api(report_id):
    """Xóa báo cáo (chỉ người tạo)."""
    try:
        user_id = int(get_jwt_identity())
    except (ValueError, TypeError):
         return jsonify(error="User ID không hợp lệ trong token"), 401

    try:
        success, message = ReportService.delete_report(report_id=report_id, user_id=user_id)
        if not success:
            status_code = 403 if "quyền" in (message or "") else 404
            return jsonify(error=message or "Không thể xóa báo cáo."), status_code
        return jsonify(message=message), 200
    except Exception as e:
        logger.error(f"Lỗi khi xóa report {report_id}: {e}", exc_info=True)
        return jsonify(error="Lỗi máy chủ nội bộ khi xóa báo cáo."), 500

# --- API Lấy danh sách báo cáo (có thể public hoặc protected) ---

@report_api.route('/reports/transaction/<int:transaction_id>', methods=['GET'])
# @jwt_required() # Bỏ comment nếu cần đăng nhập mới xem được
def get_reports_for_transaction_api(transaction_id):
    """Lấy báo cáo của một giao dịch."""
    try:
        reports = ReportService.get_reports_by_transaction(transaction_id)
        return jsonify([serialize_report(r) for r in reports]), 200
    except Exception as e:
         logger.error(f"Lỗi khi lấy reports cho transaction {transaction_id}: {e}", exc_info=True)
         return jsonify(error="Lỗi máy chủ nội bộ."), 500

@report_api.route('/reports/reported-user/<int:user_id>', methods=['GET'])
# @jwt_required()
def get_reports_about_user_api(user_id):
    """Lấy báo cáo VỀ một người dùng."""
    try:
        reports = ReportService.get_reports_about_user(user_id)
        return jsonify([serialize_report(r) for r in reports]), 200
    except Exception as e:
         logger.error(f"Lỗi khi lấy reports về user {user_id}: {e}", exc_info=True)
         return jsonify(error="Lỗi máy chủ nội bộ."), 500

@report_api.route('/reports/my-reports', methods=['GET'])
@jwt_required()
def get_my_reports_api():
    """Lấy báo cáo DO người dùng hiện tại tạo."""
    try:
        user_id = int(get_jwt_identity())
        reports = ReportService.get_reports_by_reporter(user_id)
        return jsonify([serialize_report(r) for r in reports]), 200
    except (ValueError, TypeError):
         return jsonify(error="User ID không hợp lệ trong token"), 401
    except Exception as e:
         logger.error(f"Lỗi khi lấy báo cáo của user {user_id}: {e}", exc_info=True)
         return jsonify(error="Lỗi máy chủ nội bộ."), 500

