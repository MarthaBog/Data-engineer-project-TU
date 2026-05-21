#!/usr/bin/env python3
# download_liiklus.py - Optimized: API → PostgreSQL directly (no CSV intermediate)

import os
import requests
import psycopg2
import warnings

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

def download_and_import():
    """Download CSV directly from URL and import to PostgreSQL (streaming, no temp file)."""
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
    
    # TRUNCATE table to remove old data and avoid duplicates on re-runs
    cur.execute(f"TRUNCATE TABLE {PG_TABLE} CASCADE;")
    conn.commit()
    print(f"Truncated {PG_TABLE} table")
    
    # Parse CSV stream and insert rows
    print("Importing data...")
    import csv
    import io
    
    lines = []
    row_count = 0
    
    # Buffer lines and process in chunks for better performance
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
    
    print(f"Successfully imported {row_count} rows into {PG_TABLE}")

if __name__ == "__main__":
    download_and_import()
