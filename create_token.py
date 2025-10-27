# --- File: create_token.py ---
from flask import Flask
from flask_jwt_extended import create_access_token, JWTManager

# 1. TẠO MỘT APP FLASK TẠM
app = Flask(__name__)

# 2. ĐẶT SECRET KEY (PHẢI GIỐNG HỆT TRONG FILE .env CỦA BẠN)
app.config["JWT_SECRET_KEY"] = "supersecretkey"
jwt = JWTManager(app)

# 3. TẠO TOKEN
with app.app_context():
    # Tạo một "danh tính" (identity) đặc biệt cho hệ thống.
    # Nó không cần là ID người dùng, đây là "danh tính" của service.
    system_identity = {"role": "system", "service_name": "internal_comm"}
    
    # Tạo token KHÔNG HẾT HẠN (expires_delta=False)
    system_token = create_access_token(
        identity=system_identity, 
        expires_delta=False  # Đây là cờ "vĩnh viễn"
    )
    
    # In ra màn hình, nhớ thêm "Bearer " ở đầu
    print("\n✅ TẠO TOKEN THÀNH CÔNG!")
    print("---------------------------------")
    print("SAO CHÉP TOÀN BỘ DÒNG DƯỚI ĐÂY:")
    print(f"Bearer {system_token}")
    print("---------------------------------")
    print("(Dán dòng trên vào file .env với tên INTERNAL_SERVICE_TOKEN)\n")