import pytest
from app import create_app
from app.extensions import db
import os
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture(scope="session")
def app():
    app = create_app()

    app.config.update({
        "SQLALCHEMY_DATABASE_URI": os.getenv("DATABASE_TEST_URL", ""),
        "TESTING": True
    })

    with app.app_context():
        db.drop_all()
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()