#!/usr/bin/env python3
# download_surm.py - Full reload mortality data from 2020 onwards

import os
import sys
import json
import logging
from typing import Dict, Any

import requests
import psycopg2
from pyjstat import pyjstat

# ============================================================================
# CONFIGURATION
# ============================================================================
BASE = "https://andmed.stat.ee/api/v1/et/stat/RV035"

PG_HOST = os.getenv("POSTGRES_HOST", "db")
PG_DB = os.getenv("POSTGRES_DB", "ilm_surm_liiklus")
PG_USER = os.getenv("POSTGRES_USER", "projekt")
PG_PASS = os.getenv("POSTGRES_PASSWORD", "pass")
PG_TABLE = os.getenv("SURMAD_TABLE", "surmad")

# Only download data from 2020 onwards
MIN_YEAR = "2020"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# ============================================================================
# FUNCTIONS
# ============================================================================

def get_meta() -> Dict[str, Any]:
    """Fetch metadata from Statistics Estonia API."""
    logging.info("Fetching metadata from: %s", BASE)
    r = requests.get(BASE, timeout=30)
    r.raise_for_status()
    return r.json()

def build_full_query(meta: Dict[str, Any]) -> Dict[str, Any]:
    """Build query requesting data from 2020 onwards only."""
    variables = meta.get("variables", [])
    query = []
    for v in variables:
        code = v.get("code")
        
        # For Vaatlusperiood (year), restrict to 2020 onwards
        
        if code == "Vaatlusperiood":
            values = v.get("values", [])

            if values and isinstance(values[0], dict):
                years = [val["code"] for val in values if val["code"] >= MIN_YEAR]
            else:
                years = [val for val in values if val >= MIN_YEAR]

            if years:
                query.append({"code": code, "selection": {"filter": "item", "values": years}})
            else:
                logging.warning(f"No years found >= {MIN_YEAR}")
     #   if code == "Vaatlusperiood":
     #       years = [val["code"] for val in v.get("values", []) if val["code"] >= MIN_YEAR]
     #       if years:
     #           query.append({"code": code, "selection": {"filter": "item", "values": years}})
     #       else:
     #           logging.warning(f"No years found >= {MIN_YEAR}")
        else:
            # For other dimensions, select all
            try:
                query.append({"code": code, "selection": {"filter": "all", "values": ["*"]}})
            except Exception:
                values = [val["code"] for val in v.get("values", [])]
                query.append({"code": code, "selection": {"filter": "item", "values": values}})
    
    payload = {"query": query, "response": {"format": "json-stat2"}}
    return payload

def post_query(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Send POST request and return parsed JSON."""
    logging.info("Sending query to API (this may take a while)...")
    r = requests.post(BASE, json=payload, timeout=120)
    r.raise_for_status()
    return r.json()

def jsonstat_to_rows(js: Dict[str, Any]):
    """
    Convert JSON-stat2 to rows and yield them (memory-efficient).
    Uses pyjstat library to parse the format.
    """
    try:
        datasets = pyjstat.from_json_stat(js)
        if datasets:
            # pyjstat returns DataFrame-like objects; convert to dicts
            df = datasets[0]
            if hasattr(df, 'to_dict'):
                # It's a DataFrame
                for _, row in df.iterrows():
                    yield row.to_dict()
            elif isinstance(df, list):
                # It's a list of dicts
                for row in df:
                    yield row
            else:
                # Try as dict
                for row in df:
                    yield row
    except Exception as e:
        logging.error(f"Error parsing JSON-stat2: {e}")
        raise

def import_to_postgres(json_data: Dict[str, Any]):
    """
    Stream data from JSON-stat2 directly to PostgreSQL.
    The target table is truncated first so reruns stay idempotent.
    """
    logging.info("Connecting to PostgreSQL...")
    conn = psycopg2.connect(host=PG_HOST, database=PG_DB, user=PG_USER, password=PG_PASS)
    cur = conn.cursor()
    
    # Create table if not exists
    logging.info("Creating table if not exists...")
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {PG_TABLE} (
            id SERIAL PRIMARY KEY,
            "Näitaja" TEXT,
            "Nädal" TEXT,
            "Vaatlusperiood" TEXT,
            "Sugu" TEXT,
            "Vanuserühm" TEXT,
            "value" NUMERIC
        );
    """)
    conn.commit()

    logging.info("Truncating %s before full reload...", PG_TABLE)
    cur.execute(f'TRUNCATE TABLE {PG_TABLE};')
    conn.commit()
    
    # Stream and insert rows
    logging.info("Importing data...")
    row_count = 0
    
    for row in jsonstat_to_rows(json_data):
        try:
            cur.execute(f"""
                INSERT INTO {PG_TABLE} ("Näitaja", "Nädal", "Vaatlusperiood", "Sugu", "Vanuserühm", "value")
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                str(row.get("Näitaja", "")),
                str(row.get("Nädal", "")),
                str(row.get("Vaatlusperiood", "")),
                str(row.get("Sugu", "")),
                str(row.get("Vanuserühm", "")),
                float(row.get("value", 0)) if row.get("value") else None
            ))
            row_count += 1
            
            # Batch commits for performance
            if row_count % 1000 == 0:
                conn.commit()
                logging.info(f"  {row_count} rows inserted...")
        except Exception as e:
            if row_count < 5:
                logging.error(f"Row {row_count} error: {e}, data: {row}")
            continue
    
    conn.commit()
    cur.close()
    conn.close()
    
    logging.info(f"Successfully imported {row_count} rows into {PG_TABLE}")

def main():
    """Main workflow: fetch JSON → parse → stream to PostgreSQL (2020+ only)."""
    try:
        logging.info(f"Fetching mortality data from {MIN_YEAR} onwards...")
        meta = get_meta()
        payload = build_full_query(meta)
        json_data = post_query(payload)
        import_to_postgres(json_data)
        logging.info("Done!")
    except Exception as e:
        logging.exception("Error in process")
        sys.exit(1)

if __name__ == "__main__":
    main()
