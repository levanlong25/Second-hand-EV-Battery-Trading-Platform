import sys
from app import create_app, db
from models.models import VehicleSaleData, BatterySaleData
from decimal import Decimal
import traceback

# --- DỮ LIỆU MẪU (COPY TỪ FILE CŨ) ---
# (Lưu ý: Tôi đã sửa lại giá cho đúng (thêm 3 số 0) dựa trên file mock gốc của bạn)
MOCK_VEHICLE_SALES_DATA = [
    {'brand': 'VinFast', 'model': 'VF8', 'year': 2023, 'mileage': 15000, 'sale_price': 800_000_000},
    {'brand': 'VinFast', 'model': 'VF8', 'year': 2022, 'mileage': 30000, 'sale_price': 720_000_000},
    {'brand': 'VinFast', 'model': 'VFe34', 'year': 2022, 'mileage': 40000, 'sale_price': 500_000_000},
    {'brand': 'VinFast', 'model': 'VFe34', 'year': 2023, 'mileage': 15000, 'sale_price': 550_000_000},
    {'brand': 'VinFast', 'model': 'VF9', 'year': 2023, 'mileage': 10000, 'sale_price': 1_400_000_000},
    
    {'brand': 'Tesla', 'model': 'Model 3', 'year': 2021, 'mileage': 50000, 'sale_price': 900_000_000},
    {'brand': 'Tesla', 'model': 'Model 3', 'year': 2022, 'mileage': 35000, 'sale_price': 850_000_000},
    {'brand': 'Tesla', 'model': 'Model Y', 'year': 2022, 'mileage': 25000, 'sale_price': 1_200_000_000},
    
    {'brand': 'Hyundai', 'model': 'Ioniq 5', 'year': 2022, 'mileage': 20000, 'sale_price': 1_100_000_000},
    {'brand': 'Hyundai', 'model': 'Ioniq 5', 'year': 2023, 'mileage': 5000, 'sale_price': 1_180_000_000},
    
    {'brand': 'Kia', 'model': 'EV6', 'year': 2022, 'mileage': 22000, 'sale_price': 1_150_000_000},
    {'brand': 'Kia', 'model': 'EV6', 'year': 2023, 'mileage': 10000, 'sale_price': 1_250_000_000},
    
    {'brand': 'BYD', 'model': 'Atto 3', 'year': 2023, 'mileage': 12000, 'sale_price': 950_000_000},
]

MOCK_BATTERY_SALES_DATA = [
    {'manufacturer': 'VinFast', 'capacity_kwh': 82, 'health_percent': 98, 'sale_price': 250_000_000},
    {'manufacturer': 'VinFast', 'capacity_kwh': 82, 'health_percent': 90, 'sale_price': 200_000_000},
    {'manufacturer': 'VinFast', 'capacity_kwh': 42, 'health_percent': 95, 'sale_price': 130_000_000},
    
    {'manufacturer': 'LG Chem', 'capacity_kwh': 75, 'health_percent': 95, 'sale_price': 180_000_000},
    {'manufacturer': 'LG Chem', 'capacity_kwh': 75, 'health_percent': 85, 'sale_price': 140_000_000},
    {'manufacturer': 'LG Chem', 'capacity_kwh': 80, 'health_percent': 90, 'sale_price': 170_000_000},
    
    {'manufacturer': 'CATL', 'capacity_kwh': 100, 'health_percent': 99, 'sale_price': 300_000_000},
    {'manufacturer': 'CATL', 'capacity_kwh': 100, 'health_percent': 90, 'sale_price': 260_000_000},
    {'manufacturer': 'CATL', 'capacity_kwh': 77, 'health_percent': 92, 'sale_price': 190_000_000},
    
    {'manufacturer': 'Panasonic', 'capacity_kwh': 85, 'health_percent': 97, 'sale_price': 240_000_000},
    
    {'manufacturer': 'Samsung SDI', 'capacity_kwh': 70, 'health_percent': 88, 'sale_price': 150_000_000},
]


def seed_data():
    """
    Thêm dữ liệu mẫu vào CSDL nếu CSDL trống.
    """
    app = create_app()
    with app.app_context():
        try:
            # 1. Kiểm tra xem dữ liệu đã tồn tại chưa
            if VehicleSaleData.query.first() or BatterySaleData.query.first():
                print("Dữ liệu đã tồn tại. Bỏ qua seeding.")
                return

            print("Đang thêm dữ liệu xe (Vehicle data)...")
            # 2. Thêm dữ liệu xe
            for v_data in MOCK_VEHICLE_SALES_DATA:
                vehicle = VehicleSaleData(
                    brand=v_data['brand'],
                    model=v_data['model'],
                    year=v_data['year'],
                    mileage=v_data['mileage'],
                    sale_price=float(v_data['sale_price']) # Đảm bảo là float
                )
                db.session.add(vehicle)

            print("Đang thêm dữ liệu pin (Battery data)...")
            # 3. Thêm dữ liệu pin
            for b_data in MOCK_BATTERY_SALES_DATA:
                battery = BatterySaleData(
                    manufacturer=b_data['manufacturer'],
                    capacity_kwh=float(b_data['capacity_kwh']),
                    health_percent=float(b_data['health_percent']),
                    sale_price=float(b_data['sale_price'])
                )
                db.session.add(battery)

            # 4. Commit CSDL
            db.session.commit()
            print("✅ Seeding dữ liệu thành công!")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Lỗi khi seeding dữ liệu: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

if __name__ == "__main__":
    seed_data()