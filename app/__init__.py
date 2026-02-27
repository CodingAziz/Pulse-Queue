import os
from flask import Flask
from .extensions import db

def create_app():
    app = Flask(__name__)

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, "../pulsequeue.db")

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    
    @app.route("/")
    def health():
        return {"status": "PulseQueue API running"}

    # Register blueprints
    from .routes.jobs import jobs_bp
    app.register_blueprint(jobs_bp)

    return app