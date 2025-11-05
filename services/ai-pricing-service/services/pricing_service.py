import logging
from decimal import Decimal, ROUND_HALF_UP
from app import db 
from models.models import VehicleSaleData, BatterySaleData 

logger = logging.getLogger(__name__)

PRICE_PER_YEAR_VEHICLE = Decimal('-40_000') 
PRICE_PER_KM = Decimal('-5')
GENERIC_VEHICLE_BASE_PRICE = Decimal('600_000')
GENERIC_VEHICLE_BASE_YEAR = 2022
GENERIC_VEHICLE_BASE_MILEAGE = 30000
PRICE_PER_KWH_BATTERY = Decimal('2_500')
PRICE_PER_HEALTH_PERCENT = Decimal('2_000')
GENERIC_BATTERY_BASE_PRICE = Decimal('100_000')
GENERIC_BATTERY_BASE_KWH = 60
GENERIC_BATTERY_BASE_HEALTH = 90


class PricingService:

    def _round_price(self, price): 
        return max(Decimal(0), Decimal(price).quantize(Decimal('100'), rounding=ROUND_HALF_UP))

    def _suggest_vehicle_price(self, data):
        """Gợi ý giá cho xe điện (đọc từ DB)."""
        try:
            brand = data.get('brand')
            model = data.get('model')
            year = int(data.get('year'))
            mileage = int(data.get('mileage'))

            if not all([brand, model, year, mileage]):
                return None, "Vui lòng nhập đủ thông tin xe (Hãng, Dòng, Năm, Km)."
 
            matches = VehicleSaleData.query.filter(
                VehicleSaleData.brand.ilike(brand),
                VehicleSaleData.model.ilike(model)
            ).all() 

            if matches: 
                avg_price = Decimal(sum(v.sale_price for v in matches)) / len(matches)
                avg_year = sum(v.year for v in matches) / len(matches)
                avg_mileage = sum(v.mileage for v in matches) / len(matches)
                
                year_adjustment = (Decimal(year) - Decimal(avg_year)) * PRICE_PER_YEAR_VEHICLE
                mileage_adjustment = (Decimal(mileage) - Decimal(avg_mileage)) * PRICE_PER_KM
                suggested_price = avg_price + year_adjustment + mileage_adjustment
                
                explanation = (f"Dựa trên {len(matches)} xe cùng hãng/dòng trong CSDL (giá TB {avg_price:,.0f} VNĐ), "
                               f"điều chỉnh theo năm ({year}) và số km ({mileage:,} km).")
                
                return self._round_price(suggested_price), explanation
            else:  
                logger.info(f"Không tìm thấy xe khớp {brand} {model} trong CSDL. Sử dụng logic chung.") 
                suggested_price = GENERIC_VEHICLE_BASE_PRICE + (Decimal(year) - Decimal(GENERIC_VEHICLE_BASE_YEAR)) * PRICE_PER_YEAR_VEHICLE + (Decimal(mileage) - Decimal(GENERIC_VEHICLE_BASE_MILEAGE)) * PRICE_PER_KM
                explanation = (f"Không tìm thấy dữ liệu cho {brand} {model}. "
                               f"Ước tính giá chung dựa trên năm sản xuất và số km.")
                return self._round_price(suggested_price), explanation

        except (TypeError, ValueError, AttributeError) as e:
            logger.error(f"Lỗi khi gợi ý giá xe: {e}", exc_info=True)
            return None, "Dữ liệu đầu vào không hợp lệ (ví dụ: năm, km phải là số)."
        except Exception as e:
            logger.error(f"Lỗi không xác định khi gợi ý giá xe: {e}", exc_info=True)
            return None, "Lỗi máy chủ nội bộ khi tính giá."

    def _suggest_battery_price(self, data):
        """Gợi ý giá cho pin (đọc từ DB)."""
        try:
            manufacturer = data.get('manufacturer')
            capacity_kwh = float(data.get('capacity_kwh'))
            health_percent = float(data.get('health_percent'))

            if not all([manufacturer, capacity_kwh, health_percent]):
                return None, "Vui lòng nhập đủ thông tin pin (Nhà SX, Dung lượng, Tình trạng)."
 
            matches = BatterySaleData.query.filter(
                BatterySaleData.manufacturer.ilike(manufacturer)
            ).all() 

            if matches: 
                avg_price = Decimal(sum(b.sale_price for b in matches)) / len(matches)
                avg_capacity = sum(b.capacity_kwh for b in matches) / len(matches)
                avg_health = sum(b.health_percent for b in matches) / len(matches)
                
                capacity_adjustment = (Decimal(capacity_kwh) - Decimal(avg_capacity)) * PRICE_PER_KWH_BATTERY
                health_adjustment = (Decimal(health_percent) - Decimal(avg_health)) * PRICE_PER_HEALTH_PERCENT
                suggested_price = avg_price + capacity_adjustment + health_adjustment
                
                explanation = (f"Dựa trên {len(matches)} pin cùng nhà SX trong CSDL (giá TB {avg_price:,.0f} VNĐ), "
                               f"điều chỉnh theo dung lượng ({capacity_kwh}kWh) và tình trạng ({health_percent}%).")
                
                return self._round_price(suggested_price), explanation
            else:  
                logger.info(f"Không tìm thấy pin khớp {manufacturer} trong CSDL. Sử dụng logic chung.") 
                suggested_price = GENERIC_BATTERY_BASE_PRICE + (Decimal(capacity_kwh) - Decimal(GENERIC_BATTERY_BASE_KWH)) * PRICE_PER_KWH_BATTERY + (Decimal(health_percent) - Decimal(GENERIC_BATTERY_BASE_HEALTH)) * PRICE_PER_HEALTH_PERCENT
                explanation = (f"Không tìm thấy dữ liệu cho {manufacturer}. "
                               f"Ước tính giá chung dựa trên dung lượng và tình trạng pin.")
                return self._round_price(suggested_price), explanation

        except (TypeError, ValueError, AttributeError) as e:
            logger.error(f"Lỗi khi gợi ý giá pin: {e}", exc_info=True)
            return None, "Dữ liệu đầu vào không hợp lệ (ví dụ: dung lượng, % pin phải là số)."
        except Exception as e:
            logger.error(f"Lỗi không xác định khi gợi ý giá pin: {e}", exc_info=True)
            return None, "Lỗi máy chủ nội bộ khi tính giá."

    def suggest_price(self, data): 
        listing_type = data.get('listing_type')
        if listing_type == 'vehicle':
            return self._suggest_vehicle_price(data)
        elif listing_type == 'battery':
            return self._suggest_battery_price(data)
        else:
            return None, "Loại sản phẩm không hợp lệ (chỉ hỗ trợ 'vehicle' hoặc 'battery')."

    # --- THÊM CÁC HÀM CRUD SAU CHO ADMIN ---
    
    @staticmethod
    def get_all_sales_data():
        """(Admin) Lấy tất cả dữ liệu đã bán từ DB."""
        try:
            vehicles = VehicleSaleData.query.order_by(VehicleSaleData.brand, VehicleSaleData.model).all()
            batteries = BatterySaleData.query.order_by(BatterySaleData.manufacturer).all()
            # Trả về cả hai danh sách
            return [v.to_dict() for v in vehicles], [b.to_dict() for b in batteries], None
        except Exception as e:
            logger.error(f"Lỗi khi lấy sales data: {e}", exc_info=True)
            return None, None, "Lỗi máy chủ nội bộ."
            
    @staticmethod
    def add_sale_data(data):
        """(Admin) Thêm dữ liệu bán mới vào DB."""
        listing_type = data.get('type')
        
        try:
            if listing_type == 'vehicle':
                new_data = VehicleSaleData(
                    brand=data['brand'],
                    model=data['model'],
                    year=int(data['year']),
                    mileage=int(data['mileage']),
                    sale_price=float(data['sale_price'])
                )
                db.session.add(new_data)
                db.session.commit()
                return new_data.to_dict(), None
            elif listing_type == 'battery':
                new_data = BatterySaleData(
                    manufacturer=data['manufacturer'],
                    capacity_kwh=float(data['capacity_kwh']),
                    health_percent=float(data['health_percent']),
                    sale_price=float(data['sale_price'])
                )
                db.session.add(new_data)
                db.session.commit()
                return new_data.to_dict(), None
            else:
                return None, "Loại dữ liệu không hợp lệ."
        except (KeyError, ValueError, TypeError) as e:
            db.session.rollback()
            logger.warning(f"Lỗi dữ liệu đầu vào khi thêm sale data: {e}")
            return None, "Dữ liệu đầu vào không hợp lệ hoặc thiếu trường."
        except Exception as e:
            db.session.rollback()
            logger.error(f"Lỗi DB khi thêm data: {e}", exc_info=True)
            return None, "Lỗi máy chủ nội bộ khi thêm dữ liệu."
            
    @staticmethod
    def delete_sale_data(item_type, item_id):
        """(Admin) Xóa một bản ghi dữ liệu giá."""
        try:
            item_to_delete = None
            if item_type == 'vehicle':
                item_to_delete = db.session.get(VehicleSaleData, item_id)
            elif item_type == 'battery':
                item_to_delete = db.session.get(BatterySaleData, item_id)
            else:
                return False, "Loại không hợp lệ."
                
            if not item_to_delete:
                return False, "Không tìm thấy mục."
                
            db.session.delete(item_to_delete)
            db.session.commit()
            return True, "Xóa thành công."
        except Exception as e:
            db.session.rollback()
            logger.error(f"Lỗi khi xóa data {item_type} {item_id}: {e}", exc_info=True)
            return False, "Lỗi máy chủ nội bộ."