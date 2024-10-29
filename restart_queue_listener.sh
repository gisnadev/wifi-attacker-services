#!/bin/bash

# Cek apakah proses queue listener sedang berjalan
if pgrep -x "php" | grep -q "artisan queue:listen redis --queue=default"
then
    echo "Proses queue listener sudah berjalan."
else
    echo "Proses queue listener berhenti. Memulai kembali..."
    cd /var/www/html/wifi-attacker-be
    php artisan queue:listen redis --queue=default &
fi
