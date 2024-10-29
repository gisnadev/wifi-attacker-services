#!/bin/bash

# Pindah ke direktori proyek Laravel
cd /var/www/html/wifi-attacker-be

# Jalankan perintah schedule:run
php artisan schedule:run >> /dev/null 2>&1
