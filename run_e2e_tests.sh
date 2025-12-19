#!/bin/bash
# Skrypt do uruchamiania testów E2E

set -e

echo "=== Testy E2E dla projektu AI Services ==="
echo ""

# Sprawdź czy serwisy są uruchomione
check_services() {
    echo "Sprawdzam dostępność serwisów..."

    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo "✓ Service A dostępny"
    else
        echo "✗ Service A niedostępny"
        return 1
    fi

    if curl -s http://localhost:8002/health > /dev/null 2>&1; then
        echo "✓ Service B dostępny"
    else
        echo "✗ Service B niedostępny"
        return 1
    fi

    echo ""
    return 0
}

# Uruchom testy
run_tests() {
    echo "Uruchamiam testy E2E..."
    echo ""

    cd "$(dirname "$0")"

    # Instaluj zależności jeśli potrzeba
    pip install -q -r tests/requirements.txt 2>/dev/null || true

    # Uruchom testy
    pytest tests/test_e2e.py -v --tb=short
}

# Main
if ! check_services; then
    echo ""
    echo "Uruchom serwisy przed testami E2E:"
    echo "  docker-compose up -d"
    echo ""
    exit 1
fi

run_tests

