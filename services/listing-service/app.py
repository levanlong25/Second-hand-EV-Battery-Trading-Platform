import os
import traceback
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager

load_dotenv()

db = SQLAlchemy()
migrate = Migrate(version_table='alembic_version_listings')
jwt = JWTManager()
 
from models.vehicle import Vehicle
from models.battery import Battery
from models.listing import Listing
from models.listing_image import ListingImage
from models.report import Report
from models.watchlist import WatchList

def create_app():
    app = Flask(__name__, static_folder='uploads', static_url_path='/uploads')
    CORS(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "a_very_secret_key")
    app.config['UPLOAD_FOLDER'] = 'uploads'

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from controllers.listing_controller import api_bp
    app.register_blueprint(api_bp)

    @app.errorhandler(500)
    def handle_internal_server_error(e):
        traceback.print_exc()
        if os.getenv("FLASK_ENV") == "development":
            original = getattr(e, "original_exception", e)
            return jsonify(error=f"Server Error: {str(original)}"), 500
        return jsonify(error="An internal server error occurred."), 500
    
    return app
