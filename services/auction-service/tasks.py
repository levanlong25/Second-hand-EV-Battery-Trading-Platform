# services/auction-service/tasks.py
from celery_app import celery_app  # Dòng này đã đúng từ lần trước
from services.auction_service import AuctionService # <-- ĐÃ SỬA LỖI IMPORT
import logging

logger = logging.getLogger(__name__)

# Định nghĩa task với tên đã khai báo trong beat_schedule
@celery_app.task(name='tasks.run_auction_tasks')
def run_auction_tasks():
    logger.info("Celery Task: ĐÃ NHẬN TASK, đang chạy auto_start_auctions...")
    try:
        started_count = AuctionService.auto_start_auctions()
        logger.info(f"Celery Task: Đã bắt đầu {started_count} phiên đấu giá.")
    except Exception as e:
        logger.error(f"Celery Task: Lỗi khi chạy auto_start_auctions: {e}", exc_info=True)
    
    logger.info("Celery Task: Đang chạy auto_finalize_auctions...")
    try:
        ended_count = AuctionService.auto_finalize_auctions()
        logger.info(f"Celery Task: Đã kết thúc {ended_count} phiên đấu giá.")
    except Exception as e:
        logger.error(f"Celery Task: Lỗi khi chạy auto_finalize_auctions: {e}", exc_info=True)