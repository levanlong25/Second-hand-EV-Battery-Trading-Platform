import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
import logging
 
load_dotenv()
 
jwt = JWTManager()
 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(): 
    app = Flask(__name__)
    CORS(app) 
    
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    if not app.config["JWT_SECRET_KEY"]:
        logger.warning("!!! CẢNH BÁO: JWT_SECRET_KEY chưa được đặt trong môi trường!") 
        app.config["JWT_SECRET_KEY"] = "default-dev-secret-key-admin"
 
    app.config['USER_SERVICE_URL'] = os.getenv('USER_SERVICE_URL')
    app.config['INTERNAL_API_KEY'] = os.getenv('INTERNAL_API_KEY')
    app.config['LISTING_SERVICE_URL'] = os.getenv('LISTING_SERVICE_URL')
    app.config['AUCTION_SERVICE_URL'] = os.getenv('AUCTION_SERVICE_URL')
    app.config['TRANSACTION_SERVICE_URL'] = os.getenv('TRANSACTION_SERVICE_URL')
    app.config['REVIEW_SERVICE_URL'] = os.getenv('REVIEW_SERVICE_URL') 
    app.config['REPORT_SERVICE_URL'] = os.getenv('REPORT_SERVICE_URL') 

    if not app.config['USER_SERVICE_URL'] or not app.config['LISTING_SERVICE_URL'] or not app.config['AUCTION_SERVICE_URL'] or not app.config['TRANSACTION_SERVICE_URL'] or not app.config['INTERNAL_API_KEY']:
         logger.warning("!!! CẢNH BÁO: USER_SERVICE_URL hoặc INTERNAL_API_KEY chưa được cấu hình!")

 
    jwt.init_app(app)
 
    try:
        from controllers.admin_controller import admin_bp  
        app.register_blueprint(admin_bp)
        logger.info(">>> Admin Service: Blueprint 'admin_bp' registered successfully.")
    except ImportError:
         logger.error("!!! LỖI: Không thể import 'admin_bp' từ controllers.admin_controller.")
    except Exception as e:
         logger.error(f"!!! LỖI khi đăng ký blueprint: {e}")

    logger.info(">>> Admin Service application created.")
    return app