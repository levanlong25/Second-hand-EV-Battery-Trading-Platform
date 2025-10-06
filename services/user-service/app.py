from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config.config import Config
import redis
from models.profile import Profile
from models.user import User

db = SQLAlchemy()
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses= True)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        db.create_all() 

    from controllers.auth_controller import auth_site 
    from controllers.profile_controller import profile_site  
    from controllers.user_controller import user_site 
    app.register_blueprint(user_site)
    app.register_blueprint(auth_site)
    app.register_blueprint(profile_site) 
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5001)