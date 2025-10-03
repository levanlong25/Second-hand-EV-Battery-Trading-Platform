import os

class Config:
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{os.getenv('DB_USER', 'user')}:"
        f"{os.getenv('DB_PASS', 'password')}@"
        f"{os.getenv('DB.HOST', 'localhost')}:"
        f"{os.getenv('DB.PORT', '5432')}/"
        f"{os.getenv('DB.NAME', 'users')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")