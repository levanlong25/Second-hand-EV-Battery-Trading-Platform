# services/report_service.py
from models.report import Report # Đổi tên import model
from app import db
import logging

logger = logging.getLogger(__name__)

class ReportService:

    @staticmethod
    def create_report(transaction_id, reporter_id, reported_user_id, reason, details=None):
        """Tạo báo cáo mới, kiểm tra trùng lặp và điều kiện."""
        try:
            existing_report = Report.query.filter_by(
                transaction_id=transaction_id,
                reporter_id=reporter_id,
                reported_user_id=reported_user_id
            ).first()
            if existing_report:
                return None, "Bạn đã báo cáo người dùng này cho giao dịch này rồi."
            
            allowed_reasons = ['fraud', 'misleading', 'communication', 'item_issue', 'other']
            if reason not in allowed_reasons:
                 return None, "Lý do báo cáo không hợp lệ."


            report = Report(
                transaction_id=transaction_id,
                reporter_id=reporter_id,
                reported_user_id=reported_user_id,
                reason=reason,
                details=details,
                status='pending' # Trạng thái ban đầu
            )
            db.session.add(report)
            db.session.commit()
            logger.info(f"Report {report.report_id} created successfully.")
            return report, None # Trả về report và không có lỗi

        except Exception as e:
            db.session.rollback()
            logger.error(f"Lỗi DB khi tạo report: {e}", exc_info=True)
            return None, "Lỗi cơ sở dữ liệu khi tạo báo cáo."

    @staticmethod
    def get_report_by_id(report_id):
        """Lấy báo cáo theo ID."""
        return Report.query.get(report_id)

    @staticmethod
    def get_reports_by_transaction(transaction_id):
        """Lấy các báo cáo liên quan đến một giao dịch."""
        return Report.query.filter_by(transaction_id=transaction_id).order_by(Report.created_at.desc()).all()

    @staticmethod
    def get_reports_about_user(user_id):
        """Lấy các báo cáo VỀ một người dùng."""
        return Report.query.filter_by(reported_user_id=user_id).order_by(Report.created_at.desc()).all()
      
    @staticmethod
    def get_reports_by_reporter(user_id):
         """Lấy các báo cáo DO một người dùng tạo."""
         return Report.query.filter_by(reporter_id=user_id).order_by(Report.created_at.desc()).all()

    @staticmethod
    def delete_report(report_id, user_id):
        """Xóa báo cáo, chỉ người tạo mới được xóa."""
        report = Report.query.get(report_id)
        if not report:
            return False, "Không tìm thấy báo cáo."

        if report.reporter_id != user_id:
            return False, "Bạn không có quyền xóa báo cáo này."
        
        if report.status != 'pending':
            return False, "Không thể xóa báo cáo đã được xử lý."

        try:
            db.session.delete(report)
            db.session.commit()
            logger.info(f"Report {report_id} deleted by user {user_id}.")
            return True, "Báo cáo đã được xóa thành công."
        except Exception as e:
             db.session.rollback()
             logger.error(f"Lỗi DB khi xóa report {report_id}: {e}", exc_info=True)
             return False, "Lỗi cơ sở dữ liệu khi xóa báo cáo."

    # === CÁC HÀM CHO ADMIN ===
    @staticmethod
    def get_all_reports(status_filter=None):
         """Lấy tất cả báo cáo, có thể lọc theo trạng thái."""
         query = Report.query.order_by(Report.created_at.desc())
         if status_filter and status_filter in ['pending', 'resolved', 'dismissed']:
             query = query.filter_by(status=status_filter)
         return query.all()

    @staticmethod
    def update_report_status(report_id, new_status):
         """Admin cập nhật trạng thái xử lý báo cáo."""
         report = Report.query.get(report_id)
         if not report:
             return None, "Không tìm thấy báo cáo."

         allowed_statuses = ['pending', 'resolved', 'dismissed']
         if new_status not in allowed_statuses:
              return None, "Trạng thái cập nhật không hợp lệ."

         if report.status == new_status:
              return report, f"Báo cáo đã ở trạng thái '{new_status}'."

         try:
             report.status = new_status
             db.session.commit()
             logger.info(f"Admin updated report {report_id} status to '{new_status}'.")
             return report, f"Cập nhật trạng thái báo cáo thành '{new_status}' thành công."
         except Exception as e:
              db.session.rollback()
              logger.error(f"Lỗi DB khi cập nhật status report {report_id}: {e}", exc_info=True)
              return None, "Lỗi cơ sở dữ liệu khi cập nhật trạng thái."

    @staticmethod
    def get_all_reports(status_filter=None): 
         query = Report.query.order_by(Report.created_at.desc())
         if status_filter and status_filter in ['pending', 'resolved', 'dismissed']:
             query = query.filter_by(status=status_filter)
         return query.all()

    @staticmethod
    def update_report_status(report_id, new_status): 
         report = Report.query.get(report_id)
         if not report:
             return None, "Không tìm thấy báo cáo."

         allowed_statuses = ['pending', 'resolved', 'dismissed']
         if new_status not in allowed_statuses:
              return None, "Trạng thái cập nhật không hợp lệ."

         if report.status == new_status:
              return report, f"Báo cáo đã ở trạng thái '{new_status}'."

         try:
             report.status = new_status
             db.session.commit()
             logger.info(f"Admin updated report {report_id} status to '{new_status}'.")
             return report, f"Cập nhật trạng thái báo cáo thành '{new_status}' thành công."
         except Exception as e:
              db.session.rollback()
              logger.error(f"Lỗi DB khi cập nhật status report {report_id}: {e}", exc_info=True)
              return None, "Lỗi cơ sở dữ liệu khi cập nhật trạng thái."
