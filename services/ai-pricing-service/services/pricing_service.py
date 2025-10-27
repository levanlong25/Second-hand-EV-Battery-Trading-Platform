import logging
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)

# --- KHO DỮ LIỆU GIẢ LẬP (MOCK DATA WAREHOUSE) ---
# Dữ liệu này đại diện cho các giao dịch "đã thành công"
# mà AI (logic của chúng ta) đã "học" được.
MOCK_VEHICLE_SALES_DATA = [
    # VinFast
    {'brand': 'VinFast', 'model': 'VF8', 'year': 2023, 'mileage': 15000, 'sale_price': 800_000},
    {'brand': 'VinFast', 'model': 'VF8', 'year': 2022, 'mileage': 30000, 'sale_price': 720_000},
    {'brand': 'VinFast', 'model': 'VFe34', 'year': 2022, 'mileage': 40000, 'sale_price': 500_000},
    # Tesla
    {'brand': 'Tesla', 'model': 'Model 3', 'year': 2021, 'mileage': 50000, 'sale_price': 900_000},
    {'brand': 'Tesla', 'model': 'Model Y', 'year': 2022, 'mileage': 25000, 'sale_price': 1_200_000},
    # Hyundai
    {'brand': 'Hyundai', 'model': 'Ioniq 5', 'year': 2022, 'mileage': 20000, 'sale_price': 1_100_000},
]

MOCK_BATTERY_SALES_DATA = [
    # VinFast Batteries (ví dụ)
    {'manufacturer': 'VinFast', 'capacity_kwh': 82, 'health_percent': 98, 'sale_price': 250_000},
    {'manufacturer': 'VinFast', 'capacity_kwh': 82, 'health_percent': 90, 'sale_price': 200_000},
    # LG Chem
    {'manufacturer': 'LG Chem', 'capacity_kwh': 75, 'health_percent': 95, 'sale_price': 180_000},
    {'manufacturer': 'LG Chem', 'capacity_kwh': 75, 'health_percent': 85, 'sale_price': 140_000},
    # CATL
    {'manufacturer': 'CATL', 'capacity_kwh': 100, 'health_percent': 99, 'sale_price': 300_000},
]

# --- CÁC HỆ SỐ ĐIỀU CHỈNH GIÁ (LOGIC "AI") ---
# Xe
PRICE_PER_YEAR_VEHICLE = Decimal('-40_000') # Mất giá 40tr mỗi năm
PRICE_PER_KM = Decimal('-500')                 # Mất giá 500 VND mỗi km
GENERIC_VEHICLE_BASE_PRICE = Decimal('600_000') # Giá cơ sở cho xe "loại khác"
GENERIC_VEHICLE_BASE_YEAR = 2022
GENERIC_VEHICLE_BASE_MILEAGE = 30000

# Pin
PRICE_PER_KWH_BATTERY = Decimal('2_500')  # Giá trị 2.5tr mỗi kWh
PRICE_PER_HEALTH_PERCENT = Decimal('2_000') # Giá trị 2tr mỗi % pin
GENERIC_BATTERY_BASE_PRICE = Decimal('100_000') # Giá cơ sở cho pin "loại khác"
GENERIC_BATTERY_BASE_KWH = 60
GENERIC_BATTERY_BASE_HEALTH = 90


class PricingService:

    def _round_price(self, price):
        """Làm tròn giá đến 100,000 VNĐ gần nhất."""
        return max(Decimal(0), Decimal(price).quantize(Decimal('100'), rounding=ROUND_HALF_UP))

    def _suggest_vehicle_price(self, data):
        """Gợi ý giá cho xe điện."""
        try:
            brand = data.get('brand')
            model = data.get('model')
            year = int(data.get('year'))
            mileage = int(data.get('mileage'))

            if not all([brand, model, year, mileage]):
                return None, "Vui lòng nhập đủ thông tin xe (Hãng, Dòng, Năm, Km)."
 
            matches = [v for v in MOCK_VEHICLE_SALES_DATA 
                       if v['brand'].lower() == brand.lower() and v['model'].lower() == model.lower()]

            if matches: 
                avg_price = Decimal(sum(v['sale_price'] for v in matches)) / len(matches)
                avg_year = sum(v['year'] for v in matches) / len(matches)
                avg_mileage = sum(v['mileage'] for v in matches) / len(matches)
 
                year_adjustment = (Decimal(year) - Decimal(avg_year)) * PRICE_PER_YEAR_VEHICLE
                mileage_adjustment = (Decimal(mileage) - Decimal(avg_mileage)) * PRICE_PER_KM

                suggested_price = avg_price + year_adjustment + mileage_adjustment
                
                explanation = (f"Dựa trên {len(matches)} xe cùng hãng/dòng đã bán (giá TB {avg_price:,.0f} VNĐ), "
                               f"điều chỉnh theo năm ({year}) và số km ({mileage:,} km).")
                
                return self._round_price(suggested_price), explanation

            else: 
                logger.info(f"Không tìm thấy xe khớp {brand} {model}. Sử dụng logic chung.")
 
                year_adjustment = (Decimal(year) - Decimal(GENERIC_VEHICLE_BASE_YEAR)) * PRICE_PER_YEAR_VEHICLE
                mileage_adjustment = (Decimal(mileage) - Decimal(GENERIC_VEHICLE_BASE_MILEAGE)) * PRICE_PER_KM

                suggested_price = GENERIC_VEHICLE_BASE_PRICE + year_adjustment + mileage_adjustment

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
        try:
            manufacturer = data.get('manufacturer')
            capacity_kwh = float(data.get('capacity_kwh'))
            health_percent = float(data.get('health_percent'))

            if not all([manufacturer, capacity_kwh, health_percent]):
                return None, "Vui lòng nhập đủ thông tin pin (Nhà SX, Dung lượng, Tình trạng)."
 
            matches = [b for b in MOCK_BATTERY_SALES_DATA 
                       if b['manufacturer'].lower() == manufacturer.lower()]

            if matches: 
                avg_price = Decimal(sum(b['sale_price'] for b in matches)) / len(matches)
                avg_capacity = sum(b['capacity_kwh'] for b in matches) / len(matches)
                avg_health = sum(b['health_percent'] for b in matches) / len(matches)
                 
                capacity_adjustment = (Decimal(capacity_kwh) - Decimal(avg_capacity)) * PRICE_PER_KWH_BATTERY
                health_adjustment = (Decimal(health_percent) - Decimal(avg_health)) * PRICE_PER_HEALTH_PERCENT
                
                suggested_price = avg_price + capacity_adjustment + health_adjustment
                
                explanation = (f"Dựa trên {len(matches)} pin cùng nhà SX đã bán (giá TB {avg_price:,.0f} VNĐ), "
                               f"điều chỉnh theo dung lượng ({capacity_kwh}kWh) và tình trạng ({health_percent}%).")
                
                return self._round_price(suggested_price), explanation

            else: 
                logger.info(f"Không tìm thấy pin khớp {manufacturer}. Sử dụng logic chung.")
 
                capacity_adjustment = (Decimal(capacity_kwh) - Decimal(GENERIC_BATTERY_BASE_KWH)) * PRICE_PER_KWH_BATTERY
                health_adjustment = (Decimal(health_percent) - Decimal(GENERIC_BATTERY_BASE_HEALTH)) * PRICE_PER_HEALTH_PERCENT
                
                suggested_price = GENERIC_BATTERY_BASE_PRICE + capacity_adjustment + health_adjustment
                
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
        """Hàm chính để gọi gợi ý giá."""
        listing_type = data.get('listing_type')

        if listing_type == 'vehicle':
            return self._suggest_vehicle_price(data)
        elif listing_type == 'battery':
            return self._suggest_battery_price(data)
        else:
            return None, "Loại sản phẩm không hợp lệ (chỉ hỗ trợ 'vehicle' hoặc 'battery')."
