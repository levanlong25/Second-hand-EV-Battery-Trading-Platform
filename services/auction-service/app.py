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
jwt = JWTManager()
migrate = Migrate(version_table='alembic_version_auctions')

from models.auction import Auction

def create_app(): 
    app = Flask(__name__)
    CORS(app)  
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "a-default-auction-secret-key")
 
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
 
    from controllers.auction_controller import auction_bp
    app.register_blueprint(auction_bp)
 
    @app.errorhandler(500)
    def handle_internal_server_error(e):
        traceback.print_exc()  
        if os.getenv("FLASK_ENV") == "development":
            original = getattr(e, "original_exception", e)
            return jsonify(error=f"Internal Server Error: {str(original)}"), 500
        return jsonify(error="An internal server error occurred."), 500
    
    return app
 
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5002)