docker-compose up -d --force-recreate listing-service
docker-compose up -d --build frontend
docker-compose down -v
"\\wsl.localhost\docker-desktop\mnt\docker-desktop-disk\data\docker\volumes\second-handevbatterytradingplatform_listing_uploads\_data"
docker-compose up -d --build

docker-compose exec auction-service flask db init

docker-compose exec auction-service flask db migrate -m "Initial auction service tables"

docker-compose exec auction-service flask db upgrade

docker-compose exec transaction-service flask db init

docker-compose exec transaction-service flask db migrate -m "Initial transaction service tables"

docker-compose exec transaction-service flask db upgrade

docker-compose exec user-service flask db init

docker-compose exec user-service flask db migrate -m "Initial user service tables"

docker-compose exec user-service flask db upgrade

docker-compose exec listing-service flask db init

docker-compose exec listing-service flask db migrate -m "Initial listing service tables"

docker-compose exec listing-service flask db upgrade

docker-compose exec review-service flask db init

docker-compose exec review-service flask db migrate -m "Initial review service tables"

docker-compose exec review-service flask db upgrade

docker-compose exec report-service flask db init

docker-compose exec report-service flask db migrate -m "Initial report service tables"

docker-compose exec report-service flask db upgrade

docker-compose exec user-service flask create-admin admin admin@gmail.com 08102005    


docker-compose logs -f transaction-service

docker exec -it transaction_db bash
psql -U db_user -d transaction_db
TRUNCATE TABLE transaction_db CASCADE;
TRUNCATE TABLE transaction RESTART IDENTITY CASCADE;
select * from 
UPDATE payment SET payment_status = 'initiated' WHERE payment_id = 15;
select * from payment;
DELETE FROM payment WHERE id = 1;
UPDATE auctions SET start_time = start_time::date + interval '8 hour 5 minute', end_time = start_time::date + interval '10 hour 5 minute' WHERE EXTRACT(HOUR FROM start_time) = 8;
UPDATE auctions SET auction_status = 'started' where auction_id = 1;

Service	Quản lý bảng	Chức năng chính
User Service	        Users, Profile	Đăng ký, đăng nhập, quản lý hồ sơ
Listing Service	        Listings, Vehicles, Batteries, Listing_image, Watchlist, Reports	Đăng tin, tìm kiếm, kiểm duyệt
Transaction Service	    Transactions, Payments, Fees, Digital_Contracts	Xử lý mua bán, thanh toán, hợp đồng
Review Service	        Reviews	Đánh giá, phản hồi
Auction Service     	Auctions	Đấu giá
AI Pricing Service	    (Không bảng)	Gợi ý giá bằng ML
Admin Service	        (Truy cập nhiều bảng)	Duyệt user, duyệt listing, xem báo cáo


