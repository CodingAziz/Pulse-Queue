from flask import Flask
from config import Config
from .extensions import db
from .routes.job_routes import job_bp
from app.utils.logging_config import configure_logging
from app.routes.health_routes import health_bp

def create_app():
    app = Flask(__name__)
    configure_logging()
    app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(health_bp)
    app.register_blueprint(job_bp)

    return app