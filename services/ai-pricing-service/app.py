import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
import logging

# Tải biến môi trường (từ file .env ở thư mục gốc)
load_dotenv()

# Khởi tạo extensions
jwt = JWTManager()

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Hàm khởi tạo ứng dụng Flask cho AI Pricing Service."""
    app = Flask(__name__)
    CORS(app)  
 
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    if not app.config["JWT_SECRET_KEY"]:
        logger.warning("!!! CẢNH BÁO: JWT_SECRET_KEY chưa được đặt!")
        app.config["JWT_SECRET_KEY"] = "default-dev-secret-key-pricing"  
 
    jwt.init_app(app)
 
    try:
        from controllers.pricing_controller import pricing_api
        app.register_blueprint(pricing_api)
        logger.info(">>> AI Pricing Service: Blueprint 'pricing_api' registered.")
    except ImportError:
         logger.error("!!! LỖI: Không thể import 'pricing_api' từ controllers.pricing_controller.")
    except Exception as e:
         logger.error(f"!!! LỖI khi đăng ký blueprint: {e}", exc_info=True)

    logger.info(">>> AI Pricing Service application created.")
    return app
