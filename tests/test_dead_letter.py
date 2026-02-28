def test_dead_letter_move(app):
    from app.repositories.job_repository import JobRepository
    from app.models.job import JobStatus

    with app.app_context():
        job = JobRepository.create_job(
            type="fail",
            payload={},
            max_attempts=1
        )

        JobRepository.fail_job(job, Exception("fail"))

        from app.models.dead_letter_job import DeadLetterJob

        dlq = DeadLetterJob.query.first()

        assert dlq is not None