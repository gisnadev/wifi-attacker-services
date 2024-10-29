import os
import threading
import pyrcrack
import asyncio
import os
import config
from datetime import datetime
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")


mysqlConfig = config.mysqlConfig()
pathConfig  = config.filepathConfig()
airmon = pyrcrack.AirmonNg()
firstInterface=""
secondInterface=""
thirdInterface=""
scans=[]
filePath = pathConfig['path']
file =pathConfig['file']
filePostfix = pathConfig['filePostfix']
driver  = pathConfig['driver']
async def cooper():
	for a in await airmon.interfaces:
		# global scannerInterface
		# global attackerInterface
		# if a.asdict()['driver']==driver:
		# 	if scannerInterface=="":
		# 		print(dt_string+" Scanner Interface is empty, setting it up")
		# 		scannerInterface=a.asdict()['interface']
		# 		print(dt_string+" Scanner Interface has been set up",scannerInterface)
		# 	elif scannerInterface !=a.asdict()['interface']:
		# 		print(dt_string+" attacker Interface is empty, setting it up")
		# 		attackerInterface=a.asdict()['interface']
		# 		print(dt_string+" Attacker interface has been setup", attackerInterface)
		
		global firstInterface
		global secondInterface
		global thirdInterface
		if a.asdict()['driver'] == driver:
			if firstInterface == "":
				print(dt_string + " Scanner Interface is empty, setting it up")
				firstInterface = a.asdict()['interface']
				print(dt_string + " Scanner Interface has been set up", firstInterface)
			elif secondInterface == "":
				print(dt_string + " Attacker Interface is empty, setting it up")
				secondInterface = a.asdict()['interface']
				print(dt_string + " Attacker interface has been setup", secondInterface)
			elif thirdInterface == "":  # Setting up the third interface
				print(dt_string + " Third Interface is empty, setting it up")
				thirdInterface = a.asdict()['interface']
				print(dt_string + " Third interface has been setup", thirdInterface)


def scan():
	try:
		print(dt_string+" Cleaning up previous files")
		if os.path.exists(filePath+file+"-*"):
			print(dt_string+" Its there")
			os.system("rm " + filePath + file + "-*")

	except Exception:
		print(dt_string+" file doesnt exists!")
		pass
	setMonMode(firstInterface)
	# setMonMode(attackerInterface)
	scanCommand = "sudo airodump-ng --background 1 "+firstInterface+" --write "+filePath+file
	#scanCommand = "sudo airodump-ng "+scannerInterface+" --write "+filePath+file
	os.system(scanCommand+" > /dev/null 2>&1")
def setMonMode(iface):
	monitorModeCmd = "sudo airmon-ng start "+iface
	os.system(monitorModeCmd+"  > /dev/null 2>&1")

if __name__ == '__main__':
	asyncio.run(cooper())
	if firstInterface!="":
		print(dt_string+" Scanner Interface :",firstInterface)
		scan()
	else:
		print(dt_string+" Scanner Interface Not Found!")
	if secondInterface!="":
		print(dt_string+" attacker Interface", secondInterface)
	else:
		print(dt_string+" attacker Interface Not Found!")
