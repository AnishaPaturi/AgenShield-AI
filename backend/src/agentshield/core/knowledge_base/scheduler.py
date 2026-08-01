"""
scheduler.py
------------

STEP 10 of the RAG pipeline:
Continuous Knowledge Base Updater (Task 2.2)

Purpose:
    Automatically refresh the Knowledge Base by:

        1. Running all scrapers
        2. Performing incremental ingestion
        3. Updating the Vector Database
        4. Rebuilding the BM25 index

Workflow:

        Scheduler
            ↓
      Run Scrapers
            ↓
   Download Latest Data
            ↓
 Incremental KB Update
            ↓
   Chunk Documents
            ↓
Semantic Deduplication
            ↓
 Generate Embeddings
            ↓
   Update Qdrant
            ↓
 Rebuild BM25 Index

Supports:

    • Daily scheduled refresh
    • One-time refresh (--once)
    • UTC scheduling
    • Automatic failure handling
    • Prevents overlapping jobs
    • Config-driven scheduling
"""

import sys
from datetime import datetime, timezone

from apscheduler.schedulers.blocking import BlockingScheduler

from .config import (
    SCHEDULER_COALESCE,
    SCHEDULER_MAX_INSTANCES,
    SCHEDULER_MISFIRE_GRACE_TIME,
    SCHEDULER_REFRESH_HOUR,
)
from .scrapers import run_all_scrapers
from .update_kb import incremental_update


def refresh_job() -> None:
    """
    Execute one complete refresh cycle.

    Workflow:

        Scrapers
            ↓
        Incremental Update
            ↓
        Knowledge Base Updated
    """

    print(
        f"\n[scheduler] Starting refresh at "
        f"{datetime.now(timezone.utc).isoformat()}"
    )

    try:

        run_all_scrapers()

        incremental_update()

        print(
            "[scheduler] Daily refresh completed successfully."
        )

    except Exception as e:

        print(
            f"[scheduler] Refresh failed: {e}"
        )


def start() -> None:
    """
    Start the scheduler.

    Executes refresh_job() every day at the configured hour.
    """

    scheduler = BlockingScheduler(
        timezone=timezone.utc,
    )

    scheduler.add_job(
        refresh_job,
        trigger="cron",
        hour=SCHEDULER_REFRESH_HOUR,
        id="daily_kb_refresh",
        max_instances=SCHEDULER_MAX_INSTANCES,
        coalesce=SCHEDULER_COALESCE,
        misfire_grace_time=SCHEDULER_MISFIRE_GRACE_TIME,
    )

    print(
        f"[scheduler] Daily Knowledge Base refresh scheduled "
        f"at {SCHEDULER_REFRESH_HOUR:02d}:00 UTC"
    )

    print(
        "[scheduler] Press Ctrl+C to stop."
    )

    try:

        scheduler.start()

    except (KeyboardInterrupt, SystemExit):

        print(
            "\n[scheduler] Scheduler stopped."
        )


if __name__ == "__main__":

    if "--once" in sys.argv:

        refresh_job()

    else:

        start()