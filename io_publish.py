import subprocess
import ssl
import time
import paho.mqtt.client as mqtt
import json

#grovepi 
from grovepi import *
dht_sensor_port = 7 # connect the DHt sensor to port 7
dht_sensor_type = 0 # use 0 for the blue-colored sensor and 1 for the white-colored sensor

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def on_log(client, userdata, level, buf):
	print("Debug %d: %s"%(level, buf))

def gen_payload(name, value):
	data = {}
	data['id'] = id
	data['time'] = time.strftime("%Y %m %d %H:%M:%S", time.localtime())
	data[name] = repr(value)
	#return "{\"id\":\"%s\", \"time\":\"%s\", \"%s\":\"%s\"}"%(id, time.strftime("%Y %m %d %H:%M:%S", time.localtime()), name, repr(value))
	return json.dumps(data)
	
def main():
	client = mqtt.Client("pi_john_pub")

	client.tls_set( "CARoot.pem",
					"66321288b3-certificate.pem.crt",
					"66321288b3-private.pem.key",
					cert_reqs=ssl.CERT_NONE,
					tls_version=ssl.PROTOCOL_TLSv1_2)

	client.on_connect = on_connect
	client.on_message = on_message
	#client.on_log = on_log #debug

	client.connect("a1zd8y5etgd1ze.iot.ap-northeast-1.amazonaws.com", 8883, 60)
	
	while True :
            try:

		# get the temperature and Humidity from the DHT sensor
                [ temp,hum ] = dht(dht_sensor_port,dht_sensor_type)
                client.publish("iot/temperature", payload = gen_payload("temperature", temp))
                client.publish("iot/humidity",    payload = gen_payload("humidity",    hum))
                
		# check if we have nans
		# if so, then raise a type error exception
                if isnan(temp) is True or isnan(hum) is True :
                    raise TypeError('nan error')
                
                
                sleep(1.0)
                
                
                client.disconnect()
                
                if __name__ == '__main__':
                    main()
