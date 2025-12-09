#!/bin/bash

cd /home/freeze/PycharmProjects/gpp/src

echo "=================================================="
echo "System Producent-Konsument - Demo"
echo "=================================================="
echo ""

if [ -f "tasks.csv" ]; then
    echo "Ususwanie istniejacego tasks.csv"
    rm tasks.csv
fi

echo ""
echo "[1] Uruchamianie PRODUCERA - tworzenie 100 zadań..."
python3 producer.py --count 100
echo ""

echo "[2] Uruchamianie konsumerów w tle..."
echo "    - Uruchamiam 3 konsumerów..."
echo ""

python3 consumer.py --id 1 --task-duration 30 --check-interval 5 &
CONSUMER_1_PID=$!

python3 consumer.py --id 2 --task-duration 30 --check-interval 5 &
CONSUMER_2_PID=$!

python3 consumer.py --id 3 --task-duration 30 --check-interval 5 &
CONSUMER_3_PID=$!

echo "    - Consumer 1 (PID: $CONSUMER_1_PID)"
echo "    - Consumer 2 (PID: $CONSUMER_2_PID)"
echo "    - Consumer 3 (PID: $CONSUMER_3_PID)"
echo ""
echo "Aby zatrzymać konsumery, naciśnij Ctrl+C"
echo ""

wait
