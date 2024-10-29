#!/bin/bash

# Cek apakah Laravel Echo Server sedang berjalan
if pgrep -x "laravel-echo-server" > /dev/null
then
    echo "Laravel Echo Server sudah berjalan."
else
    echo "Laravel Echo Server berhenti. Memulai kembali..."
    cd /var/www/html/wifi-attacker-be
    laravel-echo-server start
fi
