#!/bin/sh
# entrypoint.sh - Run all data download scripts sequentially
# This script is executed when the Docker container starts

set -e  # Exit on any error

echo "=== Starting data download and import ==="
echo ""

# Run traffic accident data download
echo "=== Running download_liiklus.py ==="
python download_liiklus.py

echo ""

# Run mortality statistics download
echo "=== Running download_surm.py ==="
python download_surm.py

echo ""

# Run weather data download
echo "=== Running download_ilm.py ==="
python download_ilm.py

echo ""

# Success message
echo "=== All downloads completed successfully ==="
