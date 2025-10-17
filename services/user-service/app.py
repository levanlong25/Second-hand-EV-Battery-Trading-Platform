import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
from flask_migrate import Migrate
import redis
import click

load_dotenv()

db = SQLAlchemy()
jwt = JWTManager()

migrate = Migrate(version_table='alembic_version_users')
r = None

from models.user import User
from models.profile import Profile

def create_app(): 
    app = Flask(__name__)
    CORS(app) 
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "secretkey")
 
    db.init_app(app) 
    migrate.init_app(app, db)
    jwt.init_app(app)
 
    global r
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
    try:
        r = redis.from_url(redis_url, decode_responses=True)
        r.ping()
        print(">>> User Service: Successfully connected to Redis.")
    except redis.exceptions.ConnectionError as e:
        print(f">>> User Service: Could not connect to Redis: {e}")
 
    from controllers.controllers_api import api_bp
    app.register_blueprint(api_bp)
 
    @app.cli.command("create-admin")
    @click.argument("username")
    @click.argument("email")
    @click.argument("password")
    def create_admin_command(username, email, password): 
        with app.app_context():
            from services.services_refactored import UserService
            
            if UserService.get_user_by_email_or_username(email) or UserService.get_user_by_email_or_username(username):
                print(f"Lỗi: Người dùng với email '{email}' hoặc tên đăng nhập '{username}' đã tồn tại.")
                return

            user, error = UserService.create_user(
                email=email,
                username=username,
                password=password,
                role='admin' 
            )
            if error:
                print(f"Lỗi khi tạo admin: {error}")
            else:
                print(f"Tài khoản admin '{username}' đã được tạo thành công.")
            
    return app
