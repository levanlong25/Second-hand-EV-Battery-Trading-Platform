from models.listing import Listing
from models.vehicle import Vehicle
from models.battery import Battery
from sqlalchemy.orm import joinedload
import logging

logger = logging.getLogger(__name__)

class ComparisonService:

    @staticmethod
    def get_comparison_data(listing_ids: list):
        """
        Lấy thông tin chi tiết của một danh sách các tin đăng để so sánh.
        """
        if not listing_ids:
            return None, None, "Không có ID nào được cung cấp."

        try:
            # Truy vấn tất cả listing cùng lúc
            # Dùng joinedload để Eager Load chi tiết xe/pin
            query = (
                Listing.query
                .filter(Listing.listing_id.in_(listing_ids))
                .options(joinedload(Listing.vehicle), joinedload(Listing.battery), joinedload(Listing.images))
            )
            listings = query.all()

            if not listings:
                return None, None, "Không tìm thấy tin đăng nào."

            # --- Xác thực quan trọng: Đảm bảo tất cả cùng loại ---
            first_type = listings[0].listing_type
            if not all(l.listing_type == first_type for l in listings):
                return None, None, "Chỉ có thể so sánh các sản phẩm cùng loại (xe với xe, pin với pin)."

            # Serialize dữ liệu (cần hàm serialize_listing từ controller)
            # Vì service không nên gọi controller, chúng ta sẽ trả về object
            # và để controller serialize.
            # Hoặc (đơn giản hơn cho bạn), chúng ta copy hàm serialize vào đây:
            
            serialized_data = [
                ComparisonService._serialize_for_compare(l) for l in listings
            ]

            return first_type, serialized_data, "Lấy dữ liệu so sánh thành công."

        except Exception as e:
            logger.error(f"Lỗi khi lấy dữ liệu so sánh: {e}", exc_info=True)
            return None, None, "Lỗi máy chủ nội bộ."

    @staticmethod
    def _serialize_for_compare(listing):
        """Hàm serialize rút gọn, chỉ lấy thông tin cần thiết cho so sánh."""
        if not listing: return None

        vehicle_details = None
        battery_details = None

        if listing.listing_type == 'vehicle' and listing.vehicle:
            v = listing.vehicle
            vehicle_details = {
                'brand': v.brand,
                'model': v.model,
                'year': v.year,
                'mileage': v.mileage
            }
        elif listing.listing_type == 'battery' and listing.battery:
            b = listing.battery
            battery_details = {
                'manufacturer': b.manufacturer,
                'capacity_kwh': b.capacity_kwh,
                'health_percent': b.health_percent
            }

        return {
            'listing_id': listing.listing_id,
            'listing_type': listing.listing_type,
            'title': listing.title,
            'price': str(listing.price),
            'status': listing.status,
            'images': [img.image_url for img in listing.images] if listing.images else [],
            'vehicle_details': vehicle_details,
            'battery_details': battery_details
        }


