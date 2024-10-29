import csv
from csv import DictReader
import config
import threading
import mysql.connector
from datetime import datetime
import os
#import redis
import time
#from lookup_hardware import lookup_hardware
from read_airodump import csv2blob
import re

mysqlConfig = config.mysqlConfig()
pathConfig  = config.filepathConfig()
#redisConfig = config.redisConfig()

filePath = pathConfig['path']
file =pathConfig['file']
filePostfix = pathConfig['filePostfix']
stringFile = filePath+file+filePostfix

#redthis = redis.Redis(host=redisConfig["host"], port=redisConfig["port"], db=redisConfig["db"],password=redisConfig["password"])
mysqlDb = mysql.connector.connect(
  host=mysqlConfig["host"],
  user=mysqlConfig["user"],
  database = mysqlConfig["db"],
  password=mysqlConfig["password"],
  auth_plugin='mysql_native_password'
)

mysqlCursor = mysqlDb.cursor(buffered=True)

query = "SELECT id FROM campaigns ORDER BY id DESC LIMIT 1"
mysqlCursor.execute(query)

# Mengambil ID terakhir
last_campaign_id = mysqlCursor.fetchone()[0]

def sendSocket():
     execute = 'php /var/www/html/wifighter/artisan tinker --execute="broadcast(new \App\Events\WifiFlag)"'
     #print(execute)
     os.system(execute)

def toDBApp(data):
	#print("ToDBaPP Thread",data['bssid'])
	attackmode = "normal"
	if data['enc'] =="OPN":
		attackmode ="not secure"
	query = "SELECT bssid FROM devices WHERE bssid = %s AND id_campaign = %s"
	bssid = (data['bssid'], last_campaign_id)
	mysqlCursor.execute(query, bssid)
	# query = "SELECT bssid from devices where bssid =%s"
	# bssid = (data['bssid'],)
	# mysqlCursor.execute(query, bssid)
	result = mysqlCursor.fetchone()
	time.sleep(1)
	if result is None:
		queryInsert = "INSERT INTO devices (`id_campaign`,`bssid`,`ssid`,`signal`,`channel`,`crypto`,`created_at`,`updated_at`,`type`,`attackmode`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
		insertVal = (last_campaign_id, data['bssid'], data['ssid'], data['power'], data['channel'], data['enc'], datetime.now(),datetime.now(), "Ap", attackmode)
		mysqlCursor.execute(queryInsert, insertVal)
		mysqlDb.commit()

def toDBClient(data):
	#print("Clients DB",data)
	query = "SELECT bssid ,appbssid from clients where bssid =%s AND id_campaign = %s"
	bssid = (data['bssid'], last_campaign_id)
	# query = "SELECT bssid ,appbssid from clients where bssid =%s "
	# bssid = (data['bssid'],)
	mysqlCursor.execute(query, bssid)
	result = mysqlCursor.fetchone()
	#time.sleep(1)
	if result is None:
		#print("Client empty")
		queryInsert = "INSERT INTO clients (`id_campaign`,`bssid`,`appbssid`,`signal`,`created_at`,`updated_at`) VALUES (%s,%s,%s,%s,%s,%s)"
		insertVal = (last_campaign_id, data['bssid'], data['appbssid'], data['power'], datetime.now(),datetime.now())
		mysqlCursor.execute(queryInsert, insertVal)
		mysqlDb.commit()
	# elif result is not None and result[1]!=data['appbssid']:
	# 	#print("Different associate ap isdetected, update it")
	# 	queryUpdate = "UPDATE clients set `appbssid` ='"+str(data['appbssid'])+"' , `signal`='"+str(data['power'])+"' ,`updated_at`='"+str(datetime.now())+"' where `bssid`='"+str(data['bssid'])+"'"
	# 	#print(queryUpdate)
	# 	#try:
	# 	mysqlCursor.execute(queryUpdate)
	# 	mysqlDb.commit()
def ingest():
	time.sleep(1)
	try:
		stations_list, clients_list = csv2blob(stringFile)
		nstations = len(stations_list)
		
		sthead = stations_list[0]

		stations_head = [j.strip() for j in sthead]		
		stations_data = [stations_list[i] for i in range(1, nstations)]
		for i, row in enumerate(stations_data):
			try:
				# get indices
				ap_mac_ix = stations_head.index('BSSID')
				ap_name_ix = stations_head.index('ESSID')
				ap_sec_ix = stations_head.index('Privacy')
				ap_pow_ix = stations_head.index('Power')
				ap_ch_ix = stations_head.index('channel')
				# get values
				ap_mac = row[ap_mac_ix].strip()
				ap_name = row[ap_name_ix].strip()
				ap_sec = row[ap_sec_ix].strip()
				ap_pow = row[ap_pow_ix].strip()
				ap_ch = row[ap_ch_ix].strip()
				# other stuff
				mac_prefix = ap_mac[0:8]
				# ap_mfg = lookup_hardware(mac_prefix)

				if ap_name == '':
					ap_name = "hidden"

				mac_name = re.sub('\:', '_', ap_mac)

				######################
				# Print out some information
				"""
				print("=" * 40)
				print("Name:", ap_name)
				print("Channel:", ap_ch)
				print("MAC:", ap_mac)
				# print "Manufacturer:",ap_mfg
				print("Encryption:", ap_sec)
				print("Power:", ap_pow)
				print("")"""
				dataAp={}
				dataAp['bssid'] = ap_mac
				dataAp['ssid'] = ap_name
				dataAp['channel'] =ap_ch
				dataAp['power']=ap_pow
				dataAp['enc']=ap_sec
				print(dataAp)
				if(ap_ch!="-1"):
					toDBApp(dataAp)
			except(IndexError, TypeError):
				print("Ap index of error")

		#client / Station scans
		nclients = len(clients_list)
		print("panjang client", nclients)
		clhead = clients_list[0]

		clients_head = [j.strip() for j in clhead]

		clients_data = [clients_list[i] for i in range(1, nclients)]
		for i, row in enumerate(clients_data):
			try:
				c_mac_ix = clients_head.index('Station MAC')
				c_pow_ix = clients_head.index('Power')
				c_mac_assoc = clients_head.index('BSSID')
				c_mac = row[c_mac_ix].strip()
				c_pow = row[c_pow_ix].strip()
				c_assoc_mac = row[c_mac_assoc].strip()

				if c_assoc_mac == '(not associated)':
					# print("continue because mac  not associated")
					continue
				mac_prefix = c_mac[0:8]
				# c_mfg = lookup_hardware(mac_prefix)

				######################
				# Print out some information
				# """print("=" * 40)
				# print("Client MAC:", c_mac)
				# # print "Manufacturer:",c_mfg
				# print("Power:", c_pow)
				# print("AP BSSID", c_assoc_mac)
				# print("")"""
				dataClient = {}
				dataClient['bssid'] = c_mac
				dataClient['appbssid'] = c_assoc_mac
				dataClient['power'] = c_pow
				#print("Len of appbssid",len(c_mac),"Pow",type(c_pow))
				#time.sleep(2)
				print("data client",dataClient)
				if len(c_assoc_mac) >=17:
				#if len(c_assoc_mac) >=17 and c_pow.isdecimal()==True:
					# print("data client", dataClient)
					toDBClient(dataClient)
			except (IndexError, TypeError):
				print("Client Index out of range, skip and continue")
	except Exception as e:
		print("Ingester error, continue", e)
		pass
if __name__ == '__main__':
	while True:
		ingest()
		# os.system("sudo"+"rm "+stringFile)
		# os.system("sudo"+"touch "+stringFile)
		# time.sleep(2)
		#print("Start To ingest")

