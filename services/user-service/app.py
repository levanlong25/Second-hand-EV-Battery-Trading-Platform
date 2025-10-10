import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
import redis

load_dotenv()

db = SQLAlchemy()
jwt = JWTManager()

r = None

def create_app():
    """Hàm tạo và cấu hình một instance của ứng dụng Flask (Application Factory)."""
    app = Flask(__name__)
    CORS(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

    db.init_app(app)
    jwt.init_app(app)
    
    global r
    r = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"), 
        port=int(os.getenv("REDIS_PORT", 6379)), 
        db=0,
        decode_responses=True 
    )
    try:
        r.ping()
        print(">>> Successfully connected to Redis.")
    except redis.exceptions.ConnectionError as e:
        print(f">>> Could not connect to Redis: {e}")


    with app.app_context():
        from models.user import User
        from models.profile import Profile
        db.create_all()

        from controllers.controllers_api import api_bp
        app.register_blueprint(api_bp)

        api_bp.record(app)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
