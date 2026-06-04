#!/usr/bin/env python3
"""
Pipeline Orchestrator
Coordinates: data download → dbt seed → dbt run
Uses Docker SDK instead of docker CLI
"""

import subprocess
import sys
import os
from datetime import datetime
import time

def log(msg):
    """Log with timestamp"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

def run_compose_command(cmd, description):
    """Run docker compose command"""
    log(f"Starting: {description}")
    try:
        result = subprocess.run(
            f"docker compose {cmd}",
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            cwd='/app'
        )
        log(f"✓ {description} completed")
        if result.stdout:
            log(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        log(f"✗ {description} failed with exit code {e.returncode}")
        if e.stdout:
            log(f"stdout: {e.stdout}")
        if e.stderr:
            log(f"stderr: {e.stderr}")
        return False

def main():
    log("=" * 60)
    log("PIPELINE ORCHESTRATION STARTED")
    log("=" * 60)
    
    os.chdir('/app')
    
    # Step 1: Download data (python service)
    log("\n--- Step 1: Data Download ---")
    if not run_compose_command(
        "up --remove-orphans python",
        "Data download (python service)"
    ):
        log("Data download failed. Continuing anyway...")
    
    log("\nWaiting 5 seconds before dbt seed...")
    time.sleep(5)
    
    # Step 2: DBT Seed
    log("\n--- Step 2: DBT Seed (load reference data) ---")
    if not run_compose_command(
        "--profile dbt run --rm dbt seed",
        "DBT seed"
    ):
        log("DBT seed failed, but continuing...")
    
    log("\nWaiting 5 seconds before dbt run...")
    time.sleep(5)
    
    # Step 3: DBT Run
    log("\n--- Step 3: DBT Run (transformations) ---")
    if not run_compose_command(
        "--profile dbt run --rm dbt run",
        "DBT run (transformations)"
    ):
        log("DBT run failed!")
        return False
    
    log("\n" + "=" * 60)
    log("PIPELINE ORCHESTRATION COMPLETED SUCCESSFULLY")
    log("=" * 60)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
