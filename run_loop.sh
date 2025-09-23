#!/bin/bash

# Define intervals for each task
TASK1_INTERVAL=30
TASK2_INTERVAL=60

# Get the current time in seconds since epoch
LAST_TASK1_RUN=$(date +%s)
LAST_TASK2_RUN=$(date +%s)

while true; do
    CURRENT_TIME=$(date +%s)

    # Check if it's time to run Task 1
    if [ $((CURRENT_TIME - LAST_TASK1_RUN)) -ge $TASK1_INTERVAL ]; then
        echo "Running Task 1 at $(date)"
        ./status.sh
        LAST_TASK1_RUN=$CURRENT_TIME
    fi

    # Check if it's time to run Task 2
    if [ $((CURRENT_TIME - LAST_TASK2_RUN)) -ge $TASK2_INTERVAL ]; then
        echo "Running Task 2 at $(date)"
        ./control.sh
        LAST_TASK2_RUN=$CURRENT_TIME
    fi

    # Sleep for a short period to avoid high CPU usage
    sleep 5
done
