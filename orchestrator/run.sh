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

# Step 1: Data download / ingest
log_msg ""
log_msg "--- Step 1: Data download / ingest ---"
log_msg "Running: download_liiklus.py"
python scripts/download_liiklus.py
log_msg "Running: download_surm.py"
python scripts/download_surm.py
log_msg "Running: download_ilm.py"
python scripts/download_ilm.py

log_msg "Waiting 5 seconds before dbt seed..."
sleep 5

# Step 2: DBT Seed (load reference data)
log_msg ""
log_msg "--- Step 2: DBT Seed (load reference data) ---"
log_msg "Running: dbt seed..."
dbt seed --profiles-dir . || {
    log_msg "WARNING: dbt seed had issues, continuing anyway..."
}

log_msg "Waiting 5 seconds before dbt run..."
sleep 5

# Step 3: DBT Run (transformations)
log_msg ""
log_msg "--- Step 3: DBT Run (transformations) ---"
log_msg "Running: dbt run..."
dbt run --profiles-dir . || {
    log_msg "ERROR: dbt run failed!"
    exit 1
}

log_msg "Waiting 5 seconds before dbt test..."
sleep 5

# Step 4: DBT Test (data quality)
log_msg ""
log_msg "--- Step 4: DBT Test (data quality) ---"
log_msg "Running: dbt test..."
dbt test --profiles-dir . || {
    log_msg "ERROR: dbt test failed!"
    exit 1
}

log_msg ""
log_msg "============================================================"
log_msg "PIPELINE ORCHESTRATION COMPLETED SUCCESSFULLY"
log_msg "============================================================"
