#!/bin/bash
set -e

# --- CRON ENVIRONMENT FIXES ---
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
cd /app

# Load .env file
if [ -f /app/.env ]; then
  set -a
  source /app/.env
  set +a
fi

log_msg() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log_msg "============================================================"
log_msg "PIPELINE ORCHESTRATION STARTED"
log_msg "============================================================"

# Note: Python service (data download) runs separately during compose startup
# This orchestrator handles dbt transformations on a schedule via cron

# Step 1: DBT Seed (load reference data)
log_msg ""
log_msg "--- Step 1: DBT Seed (load reference data) ---"
log_msg "Running: dbt seed..."
dbt seed --profiles-dir . || {
    log_msg "WARNING: dbt seed had issues, continuing anyway..."
}

log_msg "Waiting 5 seconds before dbt run..."
sleep 5

# Step 2: DBT Run (transformations)
log_msg ""
log_msg "--- Step 2: DBT Run (transformations) ---"
log_msg "Running: dbt run..."
dbt run --profiles-dir . || {
    log_msg "ERROR: dbt run failed!"
    exit 1
}

log_msg ""
log_msg "============================================================"
log_msg "PIPELINE ORCHESTRATION COMPLETED SUCCESSFULLY"
log_msg "============================================================"
