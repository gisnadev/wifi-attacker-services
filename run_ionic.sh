#!/bin/bash

cd /var/www/html/wifi-attacker-mobile

start_ionic() {
    echo "Memulai server Ionic di port 8100..."
    ionic serve --external
}

check_ionic() {
    if lsof -i :8100 > /dev/null; then
        echo "Server Ionic sudah berjalan di port 8100."
        return 0  # Server berjalan
    else
        echo "Server Ionic tidak berjalan di port 8100."
        return 1  # Server tidak berjalan
    fi
}

# Cek apakah server Ionic sudah berjalan
if ! check_ionic; then
    start_ionic
else
    echo "Server Ionic sudah berjalan. Tidak ada tindakan yang diperlukan."
fi
