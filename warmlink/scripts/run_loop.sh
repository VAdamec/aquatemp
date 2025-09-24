#!/bin/bash
path=$(dirname "$0":)

OPTIONS_FILE="/data/options.json"

if ! command -v jq &> /dev/null
then
    echo "jq could not be found. Please ensure it is installed."
    exit 1
fi
if [ ! -f "$OPTIONS_FILE" ]; then
    echo "options.json not found. The add-on may not be configured."
    exit 1
fi

pollintv=$(jq -r '.pollintv' "$OPTIONS_FILE")

# Get the current time in seconds since epoch
LAST_TASK_RUN=$(date +%s)

while true; do
    CURRENT_TIME=$(date +%s)

    if [ $((CURRENT_TIME - LAST_TASK_RUN)) -ge $pollintv ]; then
        echo "Running metric read process $(date)"
      	$path/heatpump info
      	$path/heatpump status
      	$path/control_heatpump
        LAST_TASK_RUN=$CURRENT_TIME
    fi

    # Sleep for a short period to avoid high CPU usage
    sleep 5
done
