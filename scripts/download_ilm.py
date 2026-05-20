#!/usr/bin/env python3
# download_ilm.py - Download daily weather data from Estonia's environmental data API
# Data source: https://keskkonnaandmed.envir.ee (f_kliima_paev)

import os
import time
import requests
import pandas as pd
import psycopg2
from urllib.parse import urlencode

# ============================================================================
# CONFIGURATION
# ============================================================================

# Estonian environmental data API base URL
BASE = "https://keskkonnaandmed.envir.ee"

# API endpoint for daily climate/weather data (f_kliima_paev = daily climate)
SERVICE = "/f_kliima_paev"

# Output file name
OUT_CSV = "ilm.csv"

# ============================================================================
# POSTGRESQL CONNECTION PARAMETERS
# ============================================================================
# Read from environment variables (set by Docker Compose)
PG_HOST = os.getenv("POSTGRES_HOST", "db")
PG_DB = os.getenv("POSTGRES_DB", "ilm_surm_liiklus")
PG_USER = os.getenv("POSTGRES_USER", "projekt")
PG_PASS = os.getenv("POSTGRES_PASSWORD", "pass")
PG_TABLE = os.getenv("ILM_TABLE", "ilm")

# ============================================================================
# FUNCTIONS
# ============================================================================

def fetch_chunk(aasta, kuu, element_kood=None, jaam_kood=None):
    """
    Fetch weather data for a specific month from the API.
    
    Args:
        aasta (int): Year (e.g., 2020)
        kuu (int): Month (1-12)
        element_kood (str, optional): Weather element code (e.g., "DTA08" for mean temp)
                                      If None, fetch all elements (may be large)
        jaam_kood (str, optional): Weather station code filter (comma-separated)
    
    Returns:
        list: JSON list of weather records
    """
    # Build query parameters using PostgREST-like syntax
    params = []
    params.append(("aasta", "eq." + str(aasta)))
    params.append(("kuu", "eq." + str(kuu)))
    
    # Add optional filters
    if element_kood:
        params.append(("element_kood", "eq." + element_kood))
    if jaam_kood:
        params.append(("jaam_kood", "in." + jaam_kood))
    
    # Build and send request
    url = BASE + SERVICE + "?" + urlencode(params)
    print(f"  URL: {url}")
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return r.json()

def rows_from_json(j):
    """
    Convert API JSON response to pandas DataFrame.
    API returns list of weather record dictionaries.
    """
    if not isinstance(j, list):
        return pd.DataFrame()
    return pd.DataFrame(j)

def save_and_import(df, csv_path):
    """
    Save DataFrame to CSV and import into PostgreSQL database.
    Creates table if it doesn't exist, then uses COPY for bulk insert.
    """
    # Export to CSV
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"CSV saved: {csv_path} ({len(df)} rows)")
    
    # Connect to database
    conn = psycopg2.connect(host=PG_HOST, database=PG_DB, user=PG_USER, password=PG_PASS)
    cur = conn.cursor()
    
    # Create table dynamically based on CSV columns (all TEXT type)
    cols = df.columns.tolist()
    col_defs = ", ".join([f"\"{c}\" TEXT" for c in cols])
    create_sql = f"CREATE TABLE IF NOT EXISTS {PG_TABLE} (id SERIAL PRIMARY KEY, {col_defs});"
    cur.execute(create_sql)
    conn.commit()
    print(f"Table {PG_TABLE} ready")
    
    # Bulk import using COPY FROM STDIN
    with open(csv_path, "r", encoding="utf-8") as f:
        col_list = ", ".join([f"\"{c}\"" for c in cols])
        copy_sql = f"COPY {PG_TABLE} ({col_list}) FROM STDIN WITH CSV HEADER DELIMITER ','"
        cur.copy_expert(copy_sql, f)
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"Imported {len(df)} rows into {PG_TABLE}")

def main(start_year, start_month, end_year, end_month, element_kood=None, jaam_kood=None):
    """
    Fetch weather data for a date range and import to database.
    Fetches data month-by-month and concatenates.
    
    Args:
        start_year (int): Start year
        start_month (int): Start month (1-12)
        end_year (int): End year
        end_month (int): End month (1-12)
        element_kood (str, optional): Weather element filter (e.g., "DTA08" = mean temp)
                                      None = all elements
        jaam_kood (str, optional): Weather station filter (comma-separated codes)
    
    Common element codes:
        DTA08 - Mean daily air temperature (°C)
        PREC - Precipitation (mm)
        TMAX - Maximum temperature (°C)
        TMIN - Minimum temperature (°C)
    """
    out_df = []
    y, m = start_year, start_month
    
    print(f"Fetching weather data from {start_year}-{start_month:02d} to {end_year}-{end_month:02d}")
    
    # Iterate through each month in range
    while (y < end_year) or (y == end_year and m <= end_month):
        print(f"Fetching {y}-{m:02d}...", end=" ")
        try:
            # Fetch data for this month
            j = fetch_chunk(y, m, element_kood=element_kood, jaam_kood=jaam_kood)
            df = rows_from_json(j)
            
            if not df.empty:
                out_df.append(df)
                print(f"OK ({len(df)} records)")
            else:
                print("No data")
            
            # Rate limit: wait 500ms between requests
            time.sleep(0.5)
        except Exception as e:
            print(f"Error: {e}")
        
        # Move to next month
        m += 1
        if m > 12:
            m = 1
            y += 1
    
    # Concatenate all monthly dataframes and import
    if out_df:
        full = pd.concat(out_df, ignore_index=True)
        print(f"\nTotal records: {len(full)}")
        save_and_import(full, OUT_CSV)
        print("Done!")
    else:
        print("No data fetched")

if __name__ == "__main__":
    # Fetch data from 2015-01 to 2024-12
    # element_kood=None: fetch all elements (temperature, precipitation, etc.)
    # jaam_kood=None: fetch all weather stations
    main(2015, 1, 2024, 12, element_kood=None, jaam_kood=None)
