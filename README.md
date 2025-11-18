docker-compose up -d --force-recreate listing-service
docker-compose up -d --build frontend
docker-compose down -v
"\\wsl.localhost\docker-desktop\mnt\docker-desktop-disk\data\docker\volumes\second-handevbatterytradingplatform_listing_uploads\_data"
<!-- lần đầu chạy -->
<!-- 1. xây dựng (build) và chạy container của chương trình ở chế độ nền -->
docker-compose up -d --build
<!-- 2. tạo và cập nhật cơ sở dữ liệu trong Flask -->
<!-- db init: khởi tạo thư mục migration. -->
<!-- db migrate: tạo file migration (các thay đổi bảng). -->
<!-- db upgrade: áp dụng migration vào database. -->
.\init_all_dbs.bat
<!-- hoặc -->
<!-- auction-service  -->
docker-compose exec auction-service flask db init
docker-compose exec auction-service flask db migrate -m "Initial auction service tables"
docker-compose exec auction-service flask db upgrade
<!-- transaction-service -->
docker-compose exec transaction-service flask db init
docker-compose exec transaction-service flask db migrate -m "Initial transaction service tables"
docker-compose exec transaction-service flask db upgrade
 <!-- user-service -->
docker-compose exec user-service flask db init
docker-compose exec user-service flask db migrate -m "Initial user service tables"
docker-compose exec user-service flask db upgrade
<!-- listing-service -->
docker-compose exec listing-service flask db init
docker-compose exec listing-service flask db migrate -m "Initial listing service tables"
docker-compose exec listing-service flask db upgrade
<!-- review-service -->
docker-compose exec review-service flask db init
docker-compose exec review-service flask db migrate -m "Initial review service tables"
docker-compose exec review-service flask db upgrade
<!-- report-service -->
docker-compose exec report-service flask db init
docker-compose exec report-service flask db migrate -m "Initial report service tables"
docker-compose exec report-service flask db upgrade

docker-compose exec ai-pricing-service flask db init
docker-compose exec ai-pricing-service flask db migrate -m "Initial ai pricing service tables"
docker-compose exec ai-pricing-service flask db upgrade
<!-- tạo tài khoản admin(có hàm trong user-service/app.py) -->
docker-compose exec user-service flask create-admin admin admin@gmail.com 08102005    
<!-- xem log (nhật ký chạy) của container(thay tên service để có thể xem log của các service khác) -->
docker-compose logs -f transaction-service
<!-- vào terminal bên trong container transaction_db(thay tên db để có thể xem log của các db khác -->
docker exec -it transaction_db bash
<!-- mở PostgreSQL CLI và kết nối vào database transaction_db(thay tên db để có thể xem log của các db khác với user db_user (POSTGRES_USER=db_user trong .env) -->
psql -U db_user -d transaction_db
<!-- xóa toàn bộ dữ liệu trong bảng -->
TRUNCATE TABLE transaction_db CASCADE;
<!-- xóa toàn bộ dữ liệu bảng transaction, đặt lại ID về 1, và xóa cả dữ liệu ở bảng liên quan (CASCADE). -->
TRUNCATE TABLE transaction RESTART IDENTITY CASCADE;
<!-- các câu lệnh truy vấn csdl -->
select * from 
INSERT INTO ... () VALUES ();
UPDATE ... SET _ = _ WHERE _ = _;
select * from ...;
DELETE FROM ... WHERE _ = _;
UPDATE auctions SET start_time = start_time::date + interval '8 hour 5 minute', end_time = start_time::date + interval '10 hour 5 minute' WHERE EXTRACT(HOUR FROM start_time) = 8;
UPDATE auctions SET auction_status = 'started' where auction_id = 1;

http://localhost:8081/nifi/
docker-compose exec ai-pricing-service python seed.py