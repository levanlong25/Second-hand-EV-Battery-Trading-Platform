# Sử dụng base image Python
FROM python:3.9-slim

# Đặt thư mục làm việc bên trong container
WORKDIR /app

# Copy file requirements trước để tận dụng cache của Docker
COPY requirements.txt .

# Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code của service vào container
COPY . .

# Lệnh để chạy ứng dụng khi container khởi động
CMD ["gunicorn", "--bind", "0.0.0.0:5002", "app:app"]
