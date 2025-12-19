#!/bin/bash
# add_100_images.sh

echo "Dodawanie 100 zdjęć do kolejki..."

for i in $(seq 1 100); do
    curl -s -X POST http://localhost:8002/analyze \
        -H "Content-Type: application/json" \
        -d "{\"image_url\": \"https://www.google.com/url?sa=t&source=web&rct=j&url=https%3A%2F%2Fwww.istockphoto.com%2Fphotos%2Fyoung-people-forest&ved=0CBUQjRxqFwoTCIi_ppCCwpEDFQAAAAAdAAAAABAH&opi=89978449\"}" \
        > /dev/null

    echo "Dodano zadanie $i/100"
done

echo "Zakończono dodawanie 100 zdjęć do kolejki"
