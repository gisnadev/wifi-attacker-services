import config
import mysql.connector
import redis
import time
import pyshark
import requests
import json
import subprocess
import pyrcrack


mysqlConfig = config.mysqlConfig()
pathConfig  = config.filepathConfig()
redisConfig = config.redisConfig()
deauthFilter = "wlan.fc.type_subtype == 0x00c"
last_campaign_id = ""
ssidVictim = ""
bssidVictim = ""
rogueAp = ""
channelRogueAp = ""
airmon = pyrcrack.AirmonNg()
driver  = pathConfig['driver']
scannerInterface=""
attackerInterface=""

async def cooper():
	for a in await airmon.interfaces:
		global scannerInterface
		global attackerInterface
		if a.asdict()['driver']==driver:
			if scannerInterface=="":
				print(" Scanner Interface is empty, setting it up")
				scannerInterface=a.asdict()['interface']
				print(" Scanner Interface has been set up",scannerInterface)
			elif scannerInterface !=a.asdict()['interface']:
				print(" attacker Interface is empty, setting it up")
				attackerInterface=a.asdict()['interface']
				print(" Attacker interface has been setup", attackerInterface)
            

#eapolFilter = "eapol"
#filter = eapolFilter
#caps = pyshark.FileCapture('/home/gifade/wifi-attacker-services/dabloo-01.cap')
caps = pyshark.LiveCapture(interface="wlx00c0cab09a17",display_filter=deauthFilter)
caps.set_debug()
caps_len = len(caps)
redthis = redis.Redis(host=redisConfig["host"], port=redisConfig["port"], db=redisConfig["db"],password=redisConfig["password"])
mysqlDb = mysql.connector.connect(
  host=mysqlConfig["host"],
  user=mysqlConfig["user"],
  database = mysqlConfig["db"],
  password=mysqlConfig["password"]
)
mysqlCursor = mysqlDb.cursor()
apiNotifications = "http://localhost:80/api/send-notification"

def lastCampaign():
  global last_campaign_id
  query = "SELECT id FROM campaigns ORDER BY id DESC LIMIT 1"
  mysqlCursor.execute(query)
  last_campaign_id = mysqlCursor.fetchone()[0]
  print("last campaign", last_campaign_id)

def getSsidVictim(bssid):
  global ssidVictim,last_campaign_id, bssidVictim
  lastCampaign()
  bssidVictim = bssid
  query = "SELECT ssid FROM devices WHERE bssid = %s AND id_campaign = %s"
  mysqlCursor.execute(query, (bssid, last_campaign_id))
  ssidVictim = mysqlCursor.fetchone()
  print("ssid victim", mysqlCursor.fetchone())

def getRogueAp():
  global ssidVictim,last_campaign_id, bssidVictim, rogueAp, channelRogueAp
  # tuple to string
  if type(ssidVictim) == tuple:
    stringSsid = ''.join(ssidVictim)
  else:
    stringSsid = ssidVictim

  query = "SELECT * FROM devices WHERE ssid = %s AND id_campaign = %s AND bssid != %s AND attackmode = %s"
  mysqlCursor.execute(query, (stringSsid, last_campaign_id, bssidVictim, "not secure"))
  dataRogueAp = mysqlCursor.fetchone()
  print("dataRogueAp", dataRogueAp)
  rogueAp = dataRogueAp[3]
  print("rogueAp", rogueAp)
  channelRogueAp = dataRogueAp[5]
  print("channelRogueAp", channelRogueAp)

def updateDb():
  global ssidVictim,last_campaign_id, bssidVictim, rogueAp, channelRogueAp
  # tuple to string
  if type(rogueAp) == tuple:
    stringRogueAp = ''.join(rogueAp)
  else:
    stringRogueAp = rogueAp
  
  if type(ssidVictim) == tuple:
    stringSsidVictim = ''.join(ssidVictim)
  else:
    stringSsidVictim = ssidVictim

  try:
    # Update database
    query = "UPDATE devices SET attackmode = 'rogue ap' WHERE id_campaign = %s AND bssid = %s;"
    mysqlCursor.execute(query, (last_campaign_id, stringRogueAp))
    mysqlDb.commit()
    
    #check setting
    query = "SELECT * FROM settings"
    mysqlCursor.execute(query)
    settingData = mysqlCursor.fetchone()
    attackStatus = settingData[1]
    tokenTele = settingData[2]
    idChatTele = settingData[3]

    # send notification telegram
    if tokenTele and idChatTele :
      query = "SELECT name FROM campaigns WHERE id = %s"
      mysqlCursor.execute(query, (last_campaign_id,))
      campaignName = mysqlCursor.fetchone()[0]
      data = {'message':  f"Fake Wifi Detected !! \nSSID <b>{stringSsidVictim}</b> detected as Fake Wifi in campaign <b>{campaignName}</b>"} 
      r = requests.post(url=apiNotifications, json=data) 
    else:
       print("Telegram Token is Empty")

    #Attack Automations
    if attackStatus == 1 :
      subprocess.run(['sudo', 'python3', 'attack.py', stringRogueAp, channelRogueAp])
    else:
      print("Attack is not automatic")

 
  except:
    print("update failed")



if __name__ == '__main__':
  time.sleep(5)
#   cooper()
  while True:
    for pkt in caps:
      if pkt.wlan.da_resolved == "ff:ff:ff:ff:ff:ff" :
        print("Transmitter",pkt.wlan.ta_resolved,"Victim",pkt.wlan.da_resolved)
      else:
         print ("Deauther Not Detected")


