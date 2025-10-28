import os
import traceback
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager

load_dotenv()

# Khởi tạo các phần mở rộng
db = SQLAlchemy()
jwt = JWTManager()
# Đặt tên bảng migrate riêng biệt cho service này
migrate = Migrate(version_table='alembic_version_transactions')

# Import models của service này
from models.transaction import Transaction
from models.payment import Payment
from models.fee import Fee
from models.fee_config import FeeConfig
from models.contract import Contract

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
    from controllers.transaction_controller import transaction_api
    from controllers.internal_controller import internal_bp
    app.register_blueprint(transaction_api)
    app.register_blueprint(internal_bp)
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "transaction service is running"}), 200
    
    @app.errorhandler(500)
    def handle_internal_server_error(e):
        traceback.print_exc() 
        if os.getenv("FLASK_ENV") == "development":
            original = getattr(e, "original_exception", e)
            return jsonify(error=f"Internal Server Error: {str(original)}"), 500
        return jsonify(error="An internal server error occurred."), 500
    
    return app

