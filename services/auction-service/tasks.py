from celery_app import celery_app
from services.auction_service import AuctionService
import logging
import requests
import os

logger = logging.getLogger(__name__)
 
NIFI_LISTENER_URL = os.environ.get('NIFI_LISTENER_URL') 
REQUEST_TIMEOUT = 5

@celery_app.task(name='tasks.run_auction_tasks')
def run_auction_tasks():
     
    logger.info("Celery Task: Đang chạy auto_start_auctions...")
    try:
        started_count = AuctionService.auto_start_auctions()
        logger.info(f"Celery Task: Đã bắt đầu {started_count} phiên đấu giá.")
    except Exception as e:
        logger.error(f"Celery Task: Lỗi khi chạy auto_start_auctions: {e}", exc_info=True)
    
    logger.info("Celery Task: Đang chạy auto_finalize_auctions (Gửi đến NiFi)...")

    if not NIFI_LISTENER_URL:
        logger.error("Celery Task: NIFI_LISTENER_URL chưa được cấu hình! Không thể gửi dữ liệu đến NiFi.")
        return "Lỗi: NIFI_LISTENER_URL chưa được cấu hình."
        
    try: 
        ended_auctions = AuctionService.get_auctions_to_finalize()
        if not ended_auctions:
            logger.info("Celery Task: Không có phiên đấu giá nào cần kết thúc.")
            return "Không có phiên đấu giá để kết thúc."

        logger.info(f"Celery Task: Tìm thấy {len(ended_auctions)} phiên đấu giá. Đang gửi đến NiFi...")
        
        success_count = 0
        fail_count = 0

        for auction in ended_auctions:
            try: 
                if not auction.winning_bidder_id:
                    logger.info(f"Celery Task: Đóng phiên đấu giá {auction.auction_id} (không có người thắng).") 
                    AuctionService.update_auction_status(auction.auction_id, 'ended')
                    success_count += 1
                    continue  
 
                payload = {
                    "auction_id": auction.auction_id,
                    "listing_id": None,  
                    "seller_id": auction.bidder_id,
                    "buyer_id": auction.winning_bidder_id,
                    "final_price": float(auction.current_bid)
                }
                 
                response = requests.post(
                    NIFI_LISTENER_URL,
                    json=payload,
                    timeout=REQUEST_TIMEOUT
                )
                 
                if 200 <= response.status_code < 300:
                    logger.info(f"Celery Task: Đã gửi thành công auction {auction.auction_id} đến NiFi.") 
                    AuctionService.update_auction_status(auction.auction_id, 'ended')
                    success_count += 1
                else: 
                    logger.error(f"Celery Task: Gửi auction {auction.auction_id} đến NiFi thất bại. Status: {response.status_code}")
                    fail_count += 1
            
            except requests.exceptions.RequestException as e: 
                logger.error(f"Celery Task: Lỗi mạng khi gửi auction {auction.auction_id} đến NiFi: {e}")
                fail_count += 1
                
        logger.info(f"Celery Task: Hoàn tất tác vụ kết thúc. Thành công: {success_count}, Thất bại (chưa gửi): {fail_count}.")
        
    except Exception as e: 
        logger.error(f"Celery Task: Lỗi nghiêm trọng trong phần auto_finalize_auctions: {e}", exc_info=True)
        return "Lỗi nghiêm trọng"
