docker-compose up -d --force-recreate listing-service
docker-compose up -d --build frontend
docker-compose down -v
"\\wsl.localhost\docker-desktop\mnt\docker-desktop-disk\data\docker\volumes\second-handevbatterytradingplatform_listing_uploads\_data"
docker-compose up -d --build

docker-compose exec user-service flask db init

docker-compose exec user-service flask db migrate -m "Initial user service tables"

docker-compose exec user-service flask db upgrade


docker-compose exec listing-service flask db init


docker-compose exec listing-service flask db migrate -m "Initial listing service tables"


docker-compose exec listing-service flask db upgrade

docker-compose exec user-service flask create-admin admin admin@gmail.com 08102005    

import logging
from logging.config import fileConfig

from flask import current_app
from alembic import context

# --- PHẦN THÊM MỚI QUAN TRỌNG ---
# Import các model của service này để biết tên bảng
# Bỏ comment các dòng dưới nếu bạn đã tạo file model tương ứng
from models.vehicle import Vehicle
from models.battery import Battery
from models.listing import Listing
from models.listing_image import ListingImage
from models.report import Report
from models.watchlist import WatchList

config = context.config
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# Lấy metadata từ ứng dụng Flask
target_metadata = current_app.extensions['migrate'].db.metadata

# Danh sách các bảng mà service này quản lý
# Alembic sẽ chỉ tạo/sửa/xóa các bảng có tên trong danh sách này
my_tables = [
    Vehicle.__tablename__,
    Battery.__tablename__,
    Listing.__tablename__,
    ListingImage.__tablename__,
    Report.__tablename__,
    WatchList.__tablename__,
]

def include_object(object, name, type_, reflected, compare_to):
    """
    Hàm này quyết định Alembic có nên "nhìn thấy" một bảng hay không.
    Nó sẽ chỉ trả về True nếu tên bảng nằm trong danh sách my_tables.
    """
    if type_ == "table" and name in my_tables:
        return True
    else:
        return False
# --- HẾT PHẦN THÊM MỚI ---


def get_engine_url():
    try:
        return current_app.extensions['migrate'].db.engine.url.render_as_string(hide_password=False).replace('%', '%%')
    except AttributeError:
        return str(current_app.extensions['migrate'].db.engine.url).replace('%', '%%')

config.set_main_option('sqlalchemy.url', get_engine_url())

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Thêm include_object vào đây để Alembic biết cần phớt lờ bảng nào
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = current_app.extensions['migrate'].db.engine
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Thêm include_object vào đây
            include_object=include_object,
            compare_type=True
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()





docker-compose exec db bash
psql -U your_db_user -d ev_trading_db
TRUNCATE TABLE listing_images CASCADE;



Service	Quản lý bảng	Chức năng chính
User Service	        Users, Profile	Đăng ký, đăng nhập, quản lý hồ sơ
Listing Service	        Listings, Vehicles, Batteries, Listing_image, Watchlist, Reports	Đăng tin, tìm kiếm, kiểm duyệt
Transaction Service	    Transactions, Payments, Fees, Digital_Contracts	Xử lý mua bán, thanh toán, hợp đồng
Review Service	        Reviews	Đánh giá, phản hồi
Auction Service     	Auctions	Đấu giá
AI Pricing Service	    (Không bảng)	Gợi ý giá bằng ML
Admin Service	        (Truy cập nhiều bảng)	Duyệt user, duyệt listing, xem báo cáo