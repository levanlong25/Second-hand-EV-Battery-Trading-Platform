from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
from config.config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    from controllers.review_controller import review_site
    app.register_blueprint(review_site)
    return app
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)