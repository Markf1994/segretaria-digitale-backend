"""Simple APScheduler setup with a sample job.

The scheduler is started on application startup from ``app.main`` and
shut down on application shutdown.  To add your own background tasks simply
define a function and register it with ``scheduler.add_job``.
"""

from apscheduler.schedulers.background import BackgroundScheduler


def sample_job() -> None:
    """Job that runs periodically and prints a message to the console."""
    # print("Sample scheduler job executed")
    pass


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

