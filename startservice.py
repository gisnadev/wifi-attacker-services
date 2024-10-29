import subprocess
import config
import time

serviceConfig  = config.filepathConfig()
servicePath = serviceConfig['service']

# Path ke dua file Python
main_script_path = servicePath+'main.py'
ingester_script_path = servicePath + 'ingester.py'
detector_script_path = servicePath + 'detector.py'
monitormode_script_path = servicePath +'toMoniotorMode.py'

# Membuat dua objek Popen untuk menjalankan kedua skrip secara non-blocking
process_monitormode = subprocess.Popen(['sudo','python3', monitormode_script_path])
time.sleep(5)
process_ingester = subprocess.Popen(['sudo','python3', ingester_script_path])
process_main = subprocess.Popen(['sudo','python3', main_script_path])
process_detector = subprocess.Popen(['sudo','python3', detector_script_path])

