# review-service/app.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
from flask_migrate import Migrate  
import logging

load_dotenv()

db = SQLAlchemy()
jwt = JWTManager()

migrate = Migrate(version_table='alembic_version_reviews')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from models.review import Review

def create_app(): 
    app = Flask(__name__)
    CORS(app)


    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "a_very_secret_key")
    app.config['INTERNAL_SERVICE_TOKEN'] = os.getenv('INTERNAL_SERVICE_TOKEN')

    db.init_app(app)
    migrate.init_app(app, db) 
    jwt.init_app(app)

    try:
        from controllers.review_controller import review_api
        from controllers.internal_controller import internal_bp
        app.register_blueprint(internal_bp)
        app.register_blueprint(review_api)
        logger.info(">>> Review Service: Blueprint 'review_api' registered.")
    except ImportError:
         logger.error("!!! LỖI: Không thể import 'review_api'.")
    except Exception as e:
         logger.error(f"!!! LỖI khi đăng ký blueprint: {e}")

    logger.info(">>> Review Service application created.")
    return app 