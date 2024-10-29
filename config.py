mysql = {
	"host":"localhost",
    "db": "fighter",
    "user": "gifade",
    "password":"190898"
}

filepath={
	"path" :"/tmp/",
	"file" :"dabloo",
	"filePostfix":"-01.csv",
	"kismet":"-01.kismet.csv",
	"kismet2":"-01.kismet.netxml",
	"log":"-01.log.csv",
	"pcap":"-01.cap",
	"driver":"88XXau",
	"service":"/home/gifade/wifi-attacker-services/"
}
redisConn={
	"host":"localhost",
	"port":6379,
	"db":1,
	"password":"Mx9!lztyua09671KP"
}
def mysqlConfig():
	return mysql
def filepathConfig():
	return filepath
def redisConfig():
	return redisConn
