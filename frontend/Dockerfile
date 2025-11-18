# Sử dụng image Nginx
FROM nginx:alpine

# Xóa file cấu hình mặc định (nếu cần)
RUN rm /etc/nginx/conf.d/default.conf

# Sao chép file cấu hình Nginx vừa tạo vào container
COPY nginx.conf /etc/nginx/conf.d/default.conf 

# Sao chép toàn bộ nội dung thư mục frontend hiện tại (index.html, scripts.js...)
# vào thư mục gốc của Nginx trong container
COPY . /usr/share/nginx/html 

# Expose cổng 80 mà Nginx lắng nghe bên trong container
EXPOSE 80

# Lệnh để khởi động Nginx
CMD ["nginx", "-g", "daemon off;"]