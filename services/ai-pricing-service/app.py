import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
import logging
from flask_sqlalchemy import SQLAlchemy    
from flask_migrate import Migrate      

load_dotenv()
 
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate(version_table='alembic_version_pricing')  

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 
from models.models import VehicleSaleData, BatterySaleData

def create_app():
    """Hàm khởi tạo ứng dụng Flask cho AI Pricing Service."""
    app = Flask(__name__)
    CORS(app)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "a-default-auction-secret-key")
    app.config['INTERNAL_SERVICE_TOKEN'] = os.getenv('INTERNAL_SERVICE_TOKEN')
     
    db.init_app(app)
    migrate.init_app(app, db)  
    jwt.init_app(app)
    
    try:
        from controllers.pricing_controller import pricing_api 
        from controllers.internal_admin_controller import internal_admin_bp
        app.register_blueprint(internal_admin_bp)
        app.register_blueprint(pricing_api)
        logger.info(">>> AI Pricing Service: Blueprint 'pricing_api' registered.")
    except ImportError:
         logger.error("!!! LỖI: Không thể import 'pricing_api' từ controllers.pricing_controller.")
    except Exception as e:
         logger.error(f"!!! LỖI khi đăng ký blueprint: {e}")

    logger.info(">>> AI Pricing Service application created.")
    return app