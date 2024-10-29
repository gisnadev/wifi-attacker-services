import pyrcrack
import config
import asyncio
import subprocess

pathConfig  = config.filepathConfig()
airmon = pyrcrack.AirmonNg()
scannerInterface=""
attackerInterface=""
driver  = pathConfig['driver']

async def cooper():
	for a in await airmon.interfaces:
		global scannerInterface
		global attackerInterface
		if a.asdict()['driver']==driver:
			if scannerInterface=="":
				scannerInterface=a.asdict()['interface']				
			elif scannerInterface !=a.asdict()['interface']:
				attackerInterface=a.asdict()['interface']
	setScanner = subprocess.Popen(['sudo', 'airmon-ng', 'start', scannerInterface ])
	setAttacker = subprocess.Popen(['sudo', 'airmon-ng', 'start', attackerInterface ])

	setScanner.wait()
	setAttacker.wait()
	
if __name__ == '__main__':
	asyncio.run(cooper())