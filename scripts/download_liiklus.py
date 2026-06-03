#!/usr/bin/env python3
# download_liiklus.py - Download only NEW traffic accident data from 2020-01-01 onwards

import os
import requests
import psycopg2
import warnings
from datetime import datetime

# Suppress SSL warnings for development (corporate proxy issue)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Avaandmete API meta-URL for traffic accident data
META_URL = "https://avaandmed.eesti.ee/api/datasets/slug/inimkannatanutega-liiklusonnetuste-andmed"

# ============================================================================
# POSTGRESQL CONNECTION PARAMETERS
# ============================================================================
PG_HOST = os.getenv("POSTGRES_HOST", "db")
PG_DB = os.getenv("POSTGRES_DB", "ilm_surm_liiklus")
PG_USER = os.getenv("POSTGRES_USER", "projekt")
PG_PASS = os.getenv("POSTGRES_PASSWORD", "pass")
PG_TABLE = "onnetused"

# Minimum date filter: only import data from 2020-01-01 onwards
MIN_DATE = "2020-01-01"

def get_download_url():
    """Fetch metadata and extract CSV download URL."""
    print("Fetching metadata...")
    response = requests.get(META_URL, verify=False, timeout=30)
    response.raise_for_status()
    
    meta = response.json()
    distributions = meta.get("distributions", [])
    
    for dist in distributions:
        if dist.get("format") == "CSV":
            access_urls = dist.get("accessUrls", [])
            if access_urls:
                return access_urls[0]
    
    raise Exception("CSV distribution not found")

def get_last_import_date(conn):
    """Get the most recent date in the database."""
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT MAX(kuupaev) FROM {PG_TABLE};")
        result = cur.fetchone()
        last_date = result[0] if result and result[0] else MIN_DATE
        return last_date
    except Exception as e:
        print(f"Could not get last import date: {e}. Starting from {MIN_DATE}")
        return MIN_DATE

def download_and_import():
    """Download CSV directly from URL and import new data to PostgreSQL."""
    url = get_download_url()
    print(f"Downloading from: {url}")
    
    # Download CSV as stream
    response = requests.get(url, verify=False, timeout=60, stream=True)
    response.raise_for_status()
    print(f"Download status: {response.status_code}")
    
    # Connect to database
    conn = psycopg2.connect(
        host=PG_HOST,
        database=PG_DB,
        user=PG_USER,
        password=PG_PASS
    )
    cur = conn.cursor()
    
    # Create table if needed
    print("Creating table if not exists...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS onnetused (
            id SERIAL PRIMARY KEY,
            kuupaev TEXT,
            kell TEXT,
            maakond TEXT,
            omavalitsus TEXT,
            hukkunud INTEGER,
            vigastatud INTEGER
        );
    """)
    conn.commit()
    
    # Get last imported date to skip existing data
    last_date = get_last_import_date(conn)
    print(f"Last imported date: {last_date}")
    print(f"Minimum date filter: {MIN_DATE}")
    
    # Parse CSV stream and insert only NEW rows
    print("Importing new data...")
    import csv
    import io
    
    lines = []
    row_count = 0
    skipped_count = 0
    
    # Buffer lines and process
    for chunk in response.iter_content(chunk_size=8192, decode_unicode=True):
        lines.append(chunk)
    
    text = ''.join(lines)
    reader = csv.DictReader(io.StringIO(text), delimiter=';')
    
    for row in reader:
        try:
            # Parse date and time
            toimumisaeg = row.get("Toimumisaeg", "")
            parts = toimumisaeg.split()
            kuupaev = parts[0] if len(parts) > 0 else ""
            kell = parts[1] if len(parts) > 1 else ""
            
            # Skip rows before minimum date
            if kuupaev < MIN_DATE:
                skipped_count += 1
                continue
            
            # Skip rows that already exist (already imported)
            if kuupaev <= last_date:
                skipped_count += 1
                continue
            
            hukkunuid = int(row.get("Hukkunuid", 0) or 0)
            vigastatuid = int(row.get("Vigastatuid", 0) or 0)
            
            cur.execute("""
                INSERT INTO onnetused (kuupaev, kell, maakond, omavalitsus, hukkunud, vigastatud)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                kuupaev,
                kell,
                row.get("Maakond", ""),
                row.get("Omavalitsus", ""),
                hukkunuid,
                vigastatuid
            ))
            row_count += 1
        except Exception as e:
            if row_count < 3:
                print(f"Row {row_count} error: {e}")
            continue
    
    conn.commit()
    cur.close()
    conn.close()
    
    print(f"Imported {row_count} NEW rows into {PG_TABLE}")
    print(f"Skipped {skipped_count} rows (before {MIN_DATE} or already existing)")

if __name__ == "__main__":
    download_and_import()
