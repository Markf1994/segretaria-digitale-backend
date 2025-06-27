"""Simple APScheduler setup with a sample job."""

from apscheduler.schedulers.background import BackgroundScheduler


def sample_job() -> None:
    """Job that runs periodically and prints a message."""
    print("Sample scheduler job executed")


scheduler = BackgroundScheduler()
scheduler.add_job(sample_job, "interval", minutes=1)


def start() -> None:
    """Start the background scheduler if it's not already running."""
    if not scheduler.running:
        scheduler.start()


def shutdown() -> None:
    """Shutdown the scheduler."""
    if scheduler.running:
        scheduler.shutdown()

