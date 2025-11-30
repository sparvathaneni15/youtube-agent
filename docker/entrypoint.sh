#!/bin/bash
set -e

MODE=$1

if [ "$MODE" = "run" ]; then
    echo "Running agent once..."
    python3 src/run_once.py

elif [ "$MODE" = "schedule" ]; then
    echo "Starting scheduler..."
    python3 src/run_scheduler.py

else
    echo "Usage: docker run youtube_agent run|schedule"
fi
