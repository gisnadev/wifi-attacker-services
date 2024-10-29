import subprocess
import config

serviceConfig  = config.filepathConfig()
servicePath = serviceConfig['service']

# Path ke dua file Python
stop_script_path = servicePath+'stop.py'
remove_script_path = servicePath+'remove.py'

# Membuat dua objek Popen untuk menjalankan kedua skrip secara non-blocking
process_stop = subprocess.Popen(['sudo','python3', stop_script_path])
process_remove = subprocess.Popen(['sudo','python3', remove_script_path])
