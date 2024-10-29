import config
import mysql.connector
import redis
import time
import pyshark
import requests
import json


mysqlConfig = config.mysqlConfig()
pathConfig  = config.filepathConfig()
redisConfig = config.redisConfig()
deauthFilter = "wlan.fc.type_subtype == 0x00c"
last_campaign_id = ""
ssidVictim = ""
bssidVictim = ""
rogueAp = ""
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
  return last_campaign_id

def getSsidVictim(bssid):
  lastCampaign()
  bssidVictim = bssid
  query = "SELECT ssid FROM devices WHERE bssid = %s AND id_campaign = %s"
  mysqlCursor.execute(query, (bssid, lastCampaign()))
  ssidVictim = mysqlCursor.fetchone()
  print("ssid victim", mysqlCursor.fetchone())

def sendNotif():
  query = "SELECT name FROM campaigns WHERE id = %s"
  mysqlCursor.execute(query, (lastCampaign(),))
  campaignName = mysqlCursor.fetchone()[0]
  data = {'message':  f"Fake Wifi Detected !! \n SSID <b>Gifade</b> detected as Fake Wifi in campaign <b>{campaignName}</b>"} 
  r = requests.post(url=apiNotifications, json=data) 

if __name__ == '__main__':
  
  sendNotif()

            

