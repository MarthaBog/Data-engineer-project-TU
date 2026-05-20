#!/usr/bin/env python3
# download_surm.py - Download mortality statistics from Statistics Estonia API
import os
import sys
import time
import json
import logging
from typing import List, Dict, Any

import requests
import pandas as pd
from pyjstat import pyjstat
import psycopg2
from psycopg2 import sql

# ============================================================================
# CONFIGURATION
# ============================================================================

# Statistics Estonia RV035 API endpoint (mortality data)
BASE = "https://andmed.stat.ee/api/v1/et/stat/RV035"

# Output file names
OUT_JSON = "surmad.json"  # Raw JSON-stat2 response
OUT_CSV = "surmad.csv"    # Converted to CSV

# Optional: split queries by dimension (set to None for single request)
CHUNK_VAR = None

# ============================================================================
# POSTGRESQL CONNECTION PARAMETERS
# ============================================================================
# Read from environment variables (set by Docker Compose)
PG_HOST = os.getenv("POSTGRES_HOST", "db")
PG_DB = os.getenv("POSTGRES_DB", "ilm_surm_liiklus")
PG_USER = os.getenv("POSTGRES_USER", "projekt")
PG_PASS = os.getenv("POSTGRES_PASSWORD", "pass")
PG_TABLE = os.getenv("SURMAD_TABLE", "surmad")

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# ============================================================================
# FUNCTIONS
# ============================================================================

def get_meta() -> Dict[str, Any]:
    """
    Fetch metadata from Statistics Estonia API to get available dimensions.
    Returns JSON with dataset structure and available values for each dimension.
    """
    logging.info("Pärin metaandmeid: %s", BASE)
    r = requests.get(BASE, timeout=30)
    r.raise_for_status()
    return r.json()

def build_full_query(meta: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a complete JSON-stat query that requests ALL available data.
    For each dimension, select all available values.
    """
    variables = meta.get("variables", [])
    query = []
    for v in variables:
        code = v.get("code")
        # Try to use "all" filter for efficiency; fallback to explicit values
        try:
            query.append({"code": code, "selection": {"filter": "all", "values": ["*"]}})
        except Exception:
            values = [val["code"] for val in v.get("values", [])]
            query.append({"code": code, "selection": {"filter": "item", "values": values}})
    
    # Wrap in payload with json-stat2 format response
    payload = {"query": query, "response": {"format": "json-stat2"}}
    return payload

def post_query(payload: Dict[str, Any]) -> bytes:
    """
    Send POST request with query payload to Statistics Estonia API.
    Returns raw bytes of the response (json-stat2 format).
    """
    logging.info("Saadan POST päringu (võib võtta aega)...")
    r = requests.post(BASE, json=payload, timeout=120)
    r.raise_for_status()
    return r.content

def save_json(content: bytes, path: str):
    """Save raw JSON response to file for reference/debugging."""
    with open(path, "wb") as f:
        f.write(content)
    logging.info("Salvestatud: %s (%d bytes)", path, len(content))

def jsonstat_to_dataframe(js: Dict[str, Any]) -> pd.DataFrame:
    """
    Convert JSON-stat2 format to pandas DataFrame using pyjstat library.
    Handles multiple dataset formats and normalizes to table structure.
    """
    # pyjstat.from_json_stat returns list of datasets
    datasets = pyjstat.from_json_stat(js)
    if not datasets:
        raise RuntimeError("json-stat teisendus ei andnud andmeid")
    
    try:
        # Try to convert first dataset to DataFrame directly
        df = pd.DataFrame(datasets[0])
    except Exception:
        # Fallback: parse using pyjstat's table structure
        table = pyjstat.pyjstat(js)
        df = pd.DataFrame(table)
    return df

def write_csv(df: pd.DataFrame, path: str):
    """Export DataFrame to CSV file."""
    df.to_csv(path, index=False, encoding="utf-8")
    logging.info("CSV kirjutatud: %s (ridu: %d, veerud: %d)", path, len(df), len(df.columns))

def import_csv_to_postgres(csv_path: str, table: str):
    """
    Import CSV file into PostgreSQL database.
    Creates table dynamically based on CSV columns (all TEXT type).
    Uses COPY FROM STDIN for efficient bulk insert.
    """
    logging.info("Impordin CSV PostgreSQL tabelisse: %s.%s", PG_DB, table)
    conn = psycopg2.connect(host=PG_HOST, database=PG_DB, user=PG_USER, password=PG_PASS)
    cur = conn.cursor()
    
    # Read CSV to determine columns
    df = pd.read_csv(csv_path, encoding="utf-8")
    cols = list(df.columns)
    
    # Build CREATE TABLE statement dynamically
    # All columns are TEXT type; adjust types as needed
    safe_cols = [c.replace('"', '').replace("'", "") for c in cols]
    col_defs = ", ".join([f"\"{c}\" TEXT" for c in safe_cols])
    create_sql = f"CREATE TABLE IF NOT EXISTS {table} (id SERIAL PRIMARY KEY, {col_defs});"
    cur.execute(create_sql)
    conn.commit()
    
    # Use COPY for bulk import (faster than INSERT)
    with open(csv_path, "r", encoding="utf-8") as f:
        try:
            col_list = ", ".join([f"\"{c}\"" for c in safe_cols])
            copy_sql = f"COPY {table} ({col_list}) FROM STDIN WITH CSV HEADER DELIMITER ',' NULL ''"
            cur.copy_expert(copy_sql, f)
            conn.commit()
            logging.info("Imporditud ridade arv: %d", len(df))
        except Exception as e:
            conn.rollback()
            logging.exception("CSV import ebaõnnestus")
            raise
    
    cur.close()
    conn.close()

def main():
    """Main workflow: fetch -> parse -> transform -> load to database."""
    try:
        # Step 1: Get metadata about available dimensions
        meta = get_meta()
        
        # Step 2: Build query requesting all data
        payload = build_full_query(meta)
        
        # Step 3: Send query to API
        content = post_query(payload)
        
        # Step 4: Save raw JSON response
        save_json(content, OUT_JSON)
        
        # Step 5: Parse JSON-stat2 to DataFrame
        js = json.loads(content.decode("utf-8"))
        df = jsonstat_to_dataframe(js)
        
        # Step 6: Handle nested structures if needed
        if isinstance(df, dict) and "value" in df:
            df = pd.DataFrame(df["value"])
        
        # Step 7: Export to CSV
        write_csv(df, OUT_CSV)
        
        # Step 8: Import CSV to PostgreSQL
        import_csv_to_postgres(OUT_CSV, PG_TABLE)
        
        logging.info("Kõik tehtud edukalt.")
    except Exception as e:
        logging.exception("Tõrge protsessis")
        sys.exit(1)

if __name__ == "__main__":
    main()
