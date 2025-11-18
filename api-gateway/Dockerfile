# Sử dụng image Nginx chính thức
FROM nginx:alpine

# Xóa file cấu hình mặc định
RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/conf.d/