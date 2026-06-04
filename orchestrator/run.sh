#!/bin/bash
set -e    # ykskõik millien käsk kukub läbi, skript peatub

# --- CRON FIXES ---
export PATH="/usr/local/bin:/usr/bin:/bin"   # cron ei leia dbt-d
cd /app                                       # cron ei tea töökausta
# --------------------------------------------

# Load .env file
if [ -f /app/.env ]; then
  export $(cat /app/.env | grep -v '^#' | xargs)
fi

log_msg() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log_msg "============================================================"
log_msg "PIPELINE ORCHESTRATION STARTED"
log_msg "============================================================"

# Step 1: Download data
log_msg ""
log_msg "--- Step 1: Data Download ---"
log_msg "Starting python service..."

# Step 2: DBT Seed
log_msg ""
log_msg "--- Step 2: DBT Seed ---"
log_msg "Running: dbt seed..."
cd /app
dbt seed --profiles-dir . || log_msg "Warning: dbt seed had issues"

log_msg "Waiting 5 seconds..."
sleep 5

# Step 3: DBT Run
log_msg ""
log_msg "--- Step 3: DBT Run (Transformations) ---"
log_msg "Running: dbt run..."
dbt run --profiles-dir . || { log_msg "ERROR: dbt run failed"; exit 1; }

log_msg ""
log_msg "============================================================"
log_msg "PIPELINE ORCHESTRATION COMPLETED SUCCESSFULLY"
log_msg "============================================================"
