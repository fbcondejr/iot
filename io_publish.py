mport subprocess
import ssl
import time
import paho.mqtt.client as mqtt
import json

from grovepi import *
dht_sensor_port = 7 # connect the DHt sensor to port 7
dht_sensor_type = 0 # use 0 for the blue-colored sensor and 1 for the white-colored sensor

id = "pi_sensehat"

#sense = SenseHat()

def get_temperature():
	temp = grovepi.get_temperature()
	cpu_temp = subprocess.check_output("vcgencmd measure_temp", shell=True)
	array = cpu_temp.split("=")
	array2 = array[1].split("'")
	cpu_tempf = float(array2[0])
	temp_calibrated = temp - ((cpu_tempf - temp)/2)

	#print('CPU_TEMP = ' + repr(cpu_tempf)) #debug
	#print('OLD_TEMP = ' + repr(temp)) #debug
	#print('NEW_TEMP = ' + repr(temp_calibrated)) #debug

	return float("{0:.1f}".format(temp_calibrated))

def get_humidity():
	return float("{0:.1f}".format(grovepi.get_humidity()))

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

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

	running = True
	while running:
		#print(get_temperature())
		#print(get_humidity())

		client.publish("iot/temperature", payload = gen_payload("temperature", get_temperature()))
		client.publish("iot/humidity",    payload = gen_payload("humidity",    get_humidity()))

		for event in grovepi.stick.get_events():
			#print("Event: {} {}".format(event.action, event.direction)) #debug
			if (event.direction == 'middle') and (event.action == 'released'):
				running = False
		time.sleep(1)

	client.disconnect()
	grovepi.clear()

if __name__ == '__main__':
	main()

