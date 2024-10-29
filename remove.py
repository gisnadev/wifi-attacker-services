import config
import os

pathConfig  = config.filepathConfig()
filePath = pathConfig['path']
file =pathConfig['file']


def remove():
	os.system(f'sudo rm {filePath}{file}*')

remove()
