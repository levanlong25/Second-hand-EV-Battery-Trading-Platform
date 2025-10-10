from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config.config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    from controllers.listing_controller import listing_site
    from controllers.battery_controller import battery_site
    from controllers.vehicle_controller import vehicle_site
    app.register_blueprint(vehicle_site)
    app.register_blueprint(battery_site)
    app.register_blueprint(listing_site)
    return app
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)  