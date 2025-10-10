from app import db

class Profile(db.Model):
    __tablename__ = "profiles"

    profile_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    full_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    avatar_url = db.Column(db.String(255))
    address = db.Column(db.Text)
    bio = db.Column(db.Text)

    user = db.relationship("User", back_populates="profile")