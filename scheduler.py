from app import create_app
from app.services.scheduler_service import SchedulerService


def main():
    app = create_app()

    with app.app_context():
        scheduler = SchedulerService()
        scheduler.start()


if __name__ == "__main__":
    main()