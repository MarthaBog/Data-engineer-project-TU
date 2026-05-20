import os
import requests
import psycopg2
import csv
import warnings

# Suppress SSL warnings for development (corporate proxy issue)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Avaandmete API meta-URL for traffic accident data
META_URL = "https://avaandmed.eesti.ee/api/datasets/slug/inimkannatanutega-liiklusonnetuste-andmed"

def download_traffic_accidents():
    """
    Download traffic accident CSV data from Estonia's open data API.
    Fetches metadata, finds CSV distribution, and saves the file locally.
    """
    print("Laen liiklusõnnetuste andmeid...")
    response = requests.get(META_URL, verify=False)
    print(f"API response status: {response.status_code}")
    
    meta = response.json()
    distributions = meta.get("distributions", [])
    print(f"Found {len(distributions)} distributions")
    
    # Find CSV distribution in the metadata
    csv_file = None
    for dist in distributions:
        if dist.get("format") == "CSV":
            csv_file = dist
            break
    
    if not csv_file:
        print(f"ERROR: CSV distribution not found.")
        raise Exception("CSV faili ei leitud metaandmetest")

    # Extract download URL from accessUrls array
    access_urls = csv_file.get("accessUrls", [])
    if not access_urls:
        raise Exception("accessUrls empty")
    
    download_url = access_urls[0]
    print(f"Download URL: {download_url}")
    
    # Download the CSV file
    csv_data = requests.get(download_url, verify=False)
    print(f"Download status: {csv_data.status_code}, Size: {len(csv_data.content)} bytes")

    # Save to local file
    with open("liiklusonnetused.csv", "wb") as f:
        f.write(csv_data.content)

    print("CSV fail alla laetud!")

def import_traffic_accidents(conn):
    """
    Import traffic accident data from CSV to PostgreSQL.
    Creates the 'onnetused' table if it doesn't exist and inserts all rows.
    """
    print("Ühendan PostgreSQL andmebaasiga...")
    
    cur = conn.cursor()

    # Create table if it doesn't exist
    print("Loon tabeli (kui puudub)...")
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

    print("Impordin CSV andmed...")
    if not os.path.exists("liiklusonnetused.csv"):
        print("ERROR: CSV file does not exist")
        return 0
    
    # Use semicolon as delimiter for Estonian CSV format
    with open("liiklusonnetused.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        rows_imported = 0
        for row in reader:
            try:
                # Parse date and time from "YYYY-MM-DD HH:MM:SS" format
                toimumisaeg = row.get("Toimumisaeg", "")
                kuupaev = toimumisaeg.split()[0] if toimumisaeg else ""
                kell = toimumisaeg.split()[1] if toimumisaeg and len(toimumisaeg.split()) > 1 else ""
                
                # Parse counts, defaulting to 0 if missing
                hukkunuid = int(row.get("Hukkunuid", 0) or 0)
                vigastatuid = int(row.get("Vigastatuid", 0) or 0)
                
                # Insert row into database
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
                rows_imported += 1
            except Exception as e:
                # Log first few errors for debugging
                if rows_imported < 3:
                    print(f"Row {rows_imported} error: {e}")
                continue

    # Commit all changes
    conn.commit()
    cur.close()
    print(f"Andmed edukalt imporditud! ({rows_imported} rows)")

if __name__ == "__main__":
    # Connect to PostgreSQL database
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "db"),
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )
    
    try:
        # Download and import traffic accident data
        download_traffic_accidents()
        import_traffic_accidents(conn)
    finally:
        conn.close()
