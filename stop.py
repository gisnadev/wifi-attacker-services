import psutil
import config

serviceConfig  = config.filepathConfig()
servicePath = serviceConfig['service']

def kill_processes_by_name(process_name):
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        if process.info['cmdline'] and process_name in ' '.join(process.info['cmdline']):
            pid = process.info['pid']
            psutil.Process(pid).terminate()

if __name__ == "__main__":
    
    process_name_to_kill = f"python3 {servicePath}"
    
    kill_processes_by_name(process_name_to_kill)
