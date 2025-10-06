from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    username = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(120), nullable = False)
    password = db.Column(db.String(128), nullable = False)
    role = db.Column(db.String(20), default = "member")
    status = db.Column(db.String(20), default = "active")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)