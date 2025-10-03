from models.user import User, db

class UserService:
    @staticmethod
    def create_user(email, username, password):
        user = User.query.filter_by(email=email).first()
        if user:
            return {"error" : "email is exists"}
        user = User.query.filter_by(username=username).first()
        if user:
            return {"error" : "username is exists"}
        user = User(username= username, email= email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()
    @staticmethod 
    def get_user_by_id(user_id):
        return User.query.get(user_id)