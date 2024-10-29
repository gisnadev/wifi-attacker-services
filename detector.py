import config
import mysql.connector
import redis
import time
import pyshark
import requests
import json
import subprocess
import pyrcrack
import asyncio


mysqlConfig = config.mysqlConfig()
pathConfig  = config.filepathConfig()
redisConfig = config.redisConfig()
deauthFilter = "wlan.fc.type_subtype == 0x00c"
last_campaign_id = ""
ssidVictim = ""
bssidVictim = ""
rogueAp = ""
bssidRogueAp =""
channelRogueAp = ""
airmon = pyrcrack.AirmonNg()
driver  = pathConfig['driver']
scannerInterface=""
attackerInterface=""
statusTele = True
caps=""

async def cooper():
	for a in await airmon.interfaces:
		global scannerInterface
		global attackerInterface
		if a.asdict()['driver']==driver:
			if scannerInterface=="":
				scannerInterface=a.asdict()['interface']
				print(" Scanner Interface has been set up",scannerInterface)
			elif scannerInterface !=a.asdict()['interface']:
				attackerInterface=a.asdict()['interface']
				print(" Attacker interface has been setup", attackerInterface)

#eapolFilter = "eapol"
#filter = eapolFilter
# caps = pyshark.FileCapture('/home/gifade/wifi-attacker-services/dabloo-01.cap')

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
  mysqlCursor.execute(query, (bssidVictim, last_campaign_id))
  ssidVictim = mysqlCursor.fetchone()
  print("ssid victim", ssidVictim)

def getRogueAp():
  global ssidVictim,last_campaign_id, bssidVictim, rogueAp, channelRogueAp,bssidRogueAp
  # tuple to string
  if type(ssidVictim) == tuple:
    stringSsid = ''.join(ssidVictim)
  else:
    stringSsid = ssidVictim

  query = "SELECT * FROM devices WHERE ssid = %s AND id_campaign = %s AND bssid != %s AND attackmode = %s"
  mysqlCursor.execute(query, (stringSsid, last_campaign_id, bssidVictim, "not secure"))
  dataRogueAp = mysqlCursor.fetchone()
  
  if dataRogueAp is not None:
    rogueAp = dataRogueAp[3]
    print("rogueAp", rogueAp)
    bssidRogueAp = dataRogueAp[2]
    print("bssidRogueAp", bssidRogueAp)
    channelRogueAp = dataRogueAp[5]
    print("channelRogueAp", channelRogueAp)

  # print("dataRogueAp", dataRogueAp)
  # rogueAp = dataRogueAp[3]
  # print("rogueAp", rogueAp)
  # bssidRogueAp = dataRogueAp[2]
  # print("bssidRogueAp", bssidRogueAp)
  # channelRogueAp = dataRogueAp[5]
  # print("channelRogueAp", channelRogueAp)

def updateDb():
  global ssidVictim,last_campaign_id, bssidVictim, rogueAp,statusTele, channelRogueAp,bssidRogueAp
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
    if bssidRogueAp != "":
      query = "UPDATE devices SET attackmode = 'rogue ap' WHERE id_campaign = %s AND bssid = %s;"
      mysqlCursor.execute(query, (last_campaign_id, bssidRogueAp))
      mysqlDb.commit()
    
      #check setting
      querySetting = "SELECT * FROM settings"
      mysqlCursor.execute(querySetting)
      settingData = mysqlCursor.fetchone()
      attackStatus = settingData[1]
      tokenTele = settingData[2]
      idChatTele = settingData[3]
      # send notification telegram
      if tokenTele and idChatTele and statusTele :
        query = "SELECT name FROM campaigns WHERE id = %s"
        mysqlCursor.execute(query, (last_campaign_id,))
        campaignName = mysqlCursor.fetchone()[0]
        data = {'message':  f"Suspect Wifi Detected !! \nSSID <b>{stringSsidVictim}</b> detected as Suspect Wifi in campaign <b>{campaignName}</b>"} 
        r = requests.post(url=apiNotifications, json=data) 
        statusTele = False
      else:
        print("Telegram Token is Empty")

      #Attack Automations
      if attackStatus == 1 :
        subprocess.run(['sudo', 'python3', 'attack.py', stringRogueAp, channelRogueAp])
      else:
        print("Attack is not automatic")

 
  except:
    print("update failed")

async def main():
    time.sleep(5)
    await cooper()
    

if __name__ == '__main__':
  loop = asyncio.get_event_loop()
  loop.run_until_complete(main())

  if attackerInterface != "":
    # print("sebelum caps")
    caps = pyshark.LiveCapture(interface=attackerInterface, display_filter=deauthFilter)
    caps.set_debug()
    while True:
      for pkt in caps:
        if pkt.wlan.da_resolved == "ff:ff:ff:ff:ff:ff":
          getSsidVictim(pkt.wlan.ta_resolved)
          getRogueAp()
          updateDb()
        else:
          print("Deauther Not Detected")
  else:
    print("attackerInterface Not Detected")
         

            

