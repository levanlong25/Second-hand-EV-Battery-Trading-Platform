import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib
import numpy as np

def train():
    """
    Hàm chính để tải dữ liệu, huấn luyện và lưu hai mô hình riêng biệt
    cho xe (vehicle) và pin (battery).
    """
    try:
        # Giả định file ev_data.csv nằm ở thư mục gốc của dự án,
        # tức là cao hơn thư mục /services/ một cấp.
        df = pd.read_csv('../../ev_data.csv')
        print("Đã tải dữ liệu thành công từ ev_data.csv")
    except FileNotFoundError:
        print("Lỗi: Không tìm thấy file 'ev_data.csv'. Hãy đảm bảo file này nằm ở thư mục gốc của dự án.")
        return

    # --- 1. Huấn luyện Mô hình cho Xe (Vehicle) ---
    print("\n--- Bắt đầu huấn luyện mô hình cho XE ---")
    df_vehicle = df[df['type'] == 'vehicle'].copy()
    
    # Xử lý các giá trị bị thiếu (nếu có)
    df_vehicle.dropna(subset=['price', 'year', 'mileage'], inplace=True)

    # Chọn đặc trưng và mục tiêu
    vehicle_features = ['brand_manufacturer', 'model', 'year', 'mileage']
    vehicle_target = 'price'

    X_vehicle = df_vehicle[vehicle_features]
    y_vehicle = df_vehicle[vehicle_target]

    # Mã hóa One-Hot
    X_vehicle_encoded = pd.get_dummies(X_vehicle, columns=['brand_manufacturer', 'model'])
    
    # Lưu lại các cột đã mã hóa để service API sử dụng
    vehicle_model_columns = X_vehicle_encoded.columns
    joblib.dump(vehicle_model_columns, 'vehicle_model_columns.pkl')
    print("Đã lưu các cột của mô hình xe vào 'vehicle_model_columns.pkl'")

    # Huấn luyện mô hình
    vehicle_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    vehicle_model.fit(X_vehicle_encoded, y_vehicle)
    print("Đã huấn luyện xong mô hình cho xe.")

    # Lưu mô hình đã huấn luyện
    joblib.dump(vehicle_model, 'vehicle_model.joblib')
    print("Đã lưu mô hình xe vào 'vehicle_model.joblib'")


    # --- 2. Huấn luyện Mô hình cho Pin (Battery) ---
    print("\n--- Bắt đầu huấn luyện mô hình cho PIN ---")
    df_battery = df[df['type'] == 'battery'].copy()

    df_battery.dropna(subset=['price', 'capacity_kwh', 'health_percent'], inplace=True)
    
    battery_features = ['brand_manufacturer', 'capacity_kwh', 'health_percent']
    battery_target = 'price'

    X_battery = df_battery[battery_features]
    y_battery = df_battery[battery_target]

    X_battery_encoded = pd.get_dummies(X_battery, columns=['brand_manufacturer'])
    
    battery_model_columns = X_battery_encoded.columns
    joblib.dump(battery_model_columns, 'battery_model_columns.pkl')
    print("Đã lưu các cột của mô hình pin vào 'battery_model_columns.pkl'")

    battery_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    battery_model.fit(X_battery_encoded, y_battery)
    print("Đã huấn luyện xong mô hình cho pin.")
    
    joblib.dump(battery_model, 'battery_model.joblib')
    print("Đã lưu mô hình pin vào 'battery_model.joblib'")
    print("\nQuá trình huấn luyện hoàn tất!")


if __name__ == '__main__':
    # Chạy hàm huấn luyện khi file này được thực thi trực tiếp
    train()
