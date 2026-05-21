#!/usr/bin/env python3
# download_ilm.py - Optimized: API JSON → PostgreSQL directly (no CSV intermediate)
# Data source: https://keskkonnaandmed.envir.ee (f_kliima_paev - daily climate data)

import os
import time
import requests
import psycopg2
from urllib.parse import urlencode

# ============================================================================
# CONFIGURATION
# ============================================================================
BASE = "https://keskkonnaandmed.envir.ee"
SERVICE = "/f_kliima_paev"

PG_HOST = os.getenv("POSTGRES_HOST", "db")
PG_DB = os.getenv("POSTGRES_DB", "ilm_surm_liiklus")
PG_USER = os.getenv("POSTGRES_USER", "projekt")
PG_PASS = os.getenv("POSTGRES_PASSWORD", "pass")
PG_TABLE = os.getenv("ILM_TABLE", "ilm")

# ============================================================================
# FUNCTIONS
# ============================================================================

def fetch_and_import_months(start_year, start_month, end_year, end_month, element_kood=None, jaam_kood=None):
    """
    Fetch weather data month-by-month from API and stream to PostgreSQL.
    Creates table schema on first successful fetch.
    """
    print(f"Fetching weather data from {start_year}-{start_month:02d} to {end_year}-{end_month:02d}")
    
    # Connect once
    conn = psycopg2.connect(
        host=PG_HOST,
        database=PG_DB,
        user=PG_USER,
        password=PG_PASS
    )
    cur = conn.cursor()
    
    # Drop table to start fresh
    print(f"Dropping {PG_TABLE} table if exists...")
    cur.execute(f"DROP TABLE IF EXISTS {PG_TABLE} CASCADE;")
    conn.commit()
    
    table_created = False
    y, m = start_year, start_month
    total_rows = 0
    
    while (y < end_year) or (y == end_year and m <= end_month):
        print(f"Fetching {y}-{m:02d}...", end=" ", flush=True)
        try:
            # Build query parameters
            params = [
                ("aasta", "eq." + str(y)),
                ("kuu", "eq." + str(m))
            ]
            if element_kood:
                params.append(("element_kood", "eq." + element_kood))
            if jaam_kood:
                params.append(("jaam_kood", "in." + jaam_kood))
            
            url = BASE + SERVICE + "?" + urlencode(params)
            r = requests.get(url, timeout=60)
            r.raise_for_status()
            data = r.json()
            
            if not isinstance(data, list) or len(data) == 0:
                print("No data")
                m += 1
                if m > 12:
                    m = 1
                    y += 1
                time.sleep(0.5)
                continue
            
            # Create table on first successful fetch (with actual data)
            if not table_created:
                print()  # newline
                print(f"Creating {PG_TABLE} table with columns from API response...")
                
                # Get column names from first row
                sample_row = data[0]
                columns = []
                for key in sample_row.keys():
                    columns.append(f'"{key}" TEXT')
                
                col_defs = ", ".join(columns)
                create_sql = f"CREATE TABLE {PG_TABLE} (id SERIAL PRIMARY KEY, {col_defs});"
                cur.execute(create_sql)
                conn.commit()
                table_created = True
                print(f"Table created with {len(sample_row)} columns")
            
            # Insert rows
            row_count = 0
            for row in data:
                try:
                    keys = list(row.keys())
                    placeholders = ", ".join(["%s"] * len(keys))
                    keys_str = ", ".join([f'"{k}"' for k in keys])
                    values = [str(row[k]) if row[k] is not None else "" for k in keys]
                    
                    sql = f"INSERT INTO {PG_TABLE} ({keys_str}) VALUES ({placeholders})"
                    cur.execute(sql, values)
                    row_count += 1
                except Exception as e:
                    if row_count < 3:
                        print(f"    Row error: {e}")
                    continue
            
            conn.commit()
            total_rows += row_count
            print(f"OK ({row_count} records) - Total: {total_rows}", flush=True)
            
        except Exception as e:
            print(f"Error: {e}")
        
        # Rate limit
        time.sleep(0.5)
        
        # Next month
        m += 1
        if m > 12:
            m = 1
            y += 1
    
    cur.close()
    conn.close()
    
    print(f"\nSuccessfully imported {total_rows} total rows into {PG_TABLE}")

if __name__ == "__main__":
    # Fetch data from 2015-01 to 2024-12
    # element_kood=None: all elements (temperature, precipitation, etc.)
    # jaam_kood=None: all weather stations
    fetch_and_import_months(2015, 1, 2024, 12, element_kood=None, jaam_kood=None)
