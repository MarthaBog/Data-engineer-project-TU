#!/usr/bin/env python3
# download_liiklus.py - Full reload traffic accident data from 2020-01-01 onwards

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

def download_and_import():
    """Download CSV directly from URL and fully reload data to PostgreSQL."""
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

    print(f"Truncating {PG_TABLE} before full reload...")
    cur.execute(f"TRUNCATE TABLE {PG_TABLE};")
    conn.commit()

    print(f"Minimum date filter: {MIN_DATE}")

    # Parse CSV stream and insert filtered rows
    print("Importing filtered data...")
    import csv
    import io
    
    lines = []
    row_count = 0
    skipped_count = 0
    seen_rows = set()
    
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
            
            hukkunuid = int(row.get("Hukkunuid", 0) or 0)
            vigastatuid = int(row.get("Vigastatuid", 0) or 0)
            natural_key = (
                kuupaev,
                kell,
                row.get("Maakond", ""),
                row.get("Omavalitsus", ""),
                hukkunuid,
                vigastatuid,
            )

            if natural_key in seen_rows:
                skipped_count += 1
                continue

            seen_rows.add(natural_key)
            
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
    
    print(f"Imported {row_count} rows into {PG_TABLE}")
    print(f"Skipped {skipped_count} rows (before {MIN_DATE})")

if __name__ == "__main__":
    download_and_import()
