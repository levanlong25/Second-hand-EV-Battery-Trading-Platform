import os

class Config:
    # Đặt DB.HOST mặc định là 'postgres-db' để Docker Compose có thể tìm thấy
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{os.getenv('DB_USER', 'user')}:"
        f"{os.getenv('DB_PASS', 'password')}@"
        f"{os.getenv('DB_HOST', 'postgres-db')}:" # Đã sửa thành DB_HOST và giá trị mặc định là 'postgres-db'
        f"{os.getenv('DB_PORT', '5432')}/"
        f"{os.getenv('DB_NAME', 'users')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")