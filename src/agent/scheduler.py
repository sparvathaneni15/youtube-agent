from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from agent.pipeline import run_pipeline

logger = logging.getLogger(__name__)


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_pipeline, "interval", hours=6, id="pipeline_run", replace_existing=True)
    scheduler.start()
    logger.info("Scheduler started; pipeline will run every 6 hours.")
    try:
        while True:
            scheduler.print_jobs()
            # Sleep handled internally by APScheduler; loop keeps process alive
            import time

            time.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Stopping scheduler...")
        scheduler.shutdown()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_scheduler()
