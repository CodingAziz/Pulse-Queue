from app import create_app
from app.services.worker_service import WorkerService


def main():
    app = create_app()

    with app.app_context():
        worker = WorkerService()
        worker.start()


if __name__ == "__main__":
    main()