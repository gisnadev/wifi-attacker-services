import subprocess
from dotenv import dotenv_values
from dotenv import set_key
import yaml
import os

envPath = "/var/www/html/wifighter/.env"
yamlPath = "/var/www/html/wifighter/config.yaml"

def set_dhcp_client_mode():
    # Set network mode to DHCP client
    with open("/etc/netplan/01-enp2s0.yaml", "w") as f:
        f.write(
            """
            network:
                version: 2
                renderer: networkd
                ethernets:
                    enp2s0:
                        dhcp4: true
            """
        )
    subprocess.run(["sudo", "netplan", "apply"])
    subprocess.run(["sudo", "systemctl", "restart", "systemd-networkd"])


def set_peer_to_peer_mode():
    # Set network mode to peer-to-peer with DHCP server
    with open("/etc/netplan/01-enp2s0.yaml", "w") as f:
        f.write(
"""
network:
  version: 2
  renderer: networkd
  ethernets:
    enp2s0:
      dhcp4: no
      addresses: [192.168.1.1/24]
      dhcp4-overrides:
        use-dns: no
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
      dhcp4-overrides:
        use-dns: false
      dhcp4: yes
"""
        )
    subprocess.run(["sudo", "netplan", "apply"])
    subprocess.run(["sudo", "systemctl", "restart", "systemd-networkd"])

def toggle_network_mode(conf):
    # Check the current network mode
    res = subprocess.run(["nmcli", "connection", "show"], capture_output=True, text=True)
    if conf == "peer-to-peer":
        set_peer_to_peer_mode()
        print("Network mode set to peer-to-peer with DHCP server")
    else:
        set_dhcp_client_mode()
        print("Network mode set dynamic dhcp client")

if __name__ == "__main__":
    print('Listening Like no one singing..')
    with open(yamlPath, 'r') as stream:
        yaml_data = yaml.safe_load(stream)

        # Check if the ISEDITED key is 1
    if yaml_data.get('ISEDITED') == 1:
            # Open the .env file in read mode
        with open(envPath, 'r') as env_file:
                # Read the existing key-value pairs into a dictionary
            env_dict = {}
            for line in env_file:
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_dict[key.strip()] = value.strip()
        with open(envPath, 'r') as env_file:
            env_lines = env_file.readlines()
        with open(envPath, 'a') as env_file:
                # Check if each YAML key exists in the .env file
            for key, value in yaml_data.items():
                if key != 'ISEDITED':
                    if key not in env_dict:
                        print("Key is not there for",key)
                            # Append the key-value pair if it doesn't already exist
                        env_file.write(f'{key}={value}\n')
                    else:
                        print(env_dict)
                        #print(key," Key is exist",env_dict[key],"isinya ",value)
                            # Update the key-value pair if it already exists
                        updated_lines = []
                        for line in env_lines:
                            print("line",line)
                            #print(line,"f loops",key)
                            if line.startswith(f'{key}='):
                                print("my line",line)
                                line = f'{key}={value}\n'
                            updated_lines.append(line)
                        env_file.seek(0)
                        env_file.truncate(0)
                        env_file.write(''.join(updated_lines))

    skip = 0
    while skip==1:
        env_vars = dotenv_values(envPath)
        print('Listening Like no one singing..')
        networkIsEdit      = env_vars.get("NETWORK_ISEDIT")
        networkRequestConf = env_vars.get("NETWORK_TYPE")
        print("Is Network Edited?",networkIsEdit)
        if int(networkIsEdit) ==1:
            print("Network is edit , with request conf",networkRequestConf)
            toggle_network_mode(networkRequestConf)
            set_key(envPath, "NETWORK_ISEDIT", "0")
        else:
            print("Network is ok")
    #toggle_network_mode()

