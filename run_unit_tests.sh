#!/bin/bash
# Skrypt do uruchamiania wszystkich testów

set -e

echo "=== Testy jednostkowe i integracyjne ==="
echo ""

cd "$(dirname "$0")"

# Testy Service A
echo "--- Testy Service A ---"
cd service_a
pip install -q -r requirements.txt 2>/dev/null || true
pytest test_integration.py -v --tb=short
cd ..

echo ""
echo "--- Testy Service B ---"
cd service_b
pip install -q -r requirements.txt 2>/dev/null || true
pytest test_integration.py -v --tb=short
cd ..

echo ""
echo "=== Wszystkie testy jednostkowe przeszły! ==="

