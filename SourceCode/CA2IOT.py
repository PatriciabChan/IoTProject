# Import SDK packages
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from time import sleep
from gpiozero import Motor, Buzzer, LED, InputDevice, Button, MCP3008
from signal import pause
import sys
import Adafruit_DHT
from rpi_lcd import LCD
import time, datetime
import boto3
import botocore

s3 = boto3.resource('s3')
motor2 = Motor(20,22, pwm = True)
adc = MCP3008(channel=0)
temppin = 19
lcd = LCD()
led = LED(24)
full_path = '/home/pi/Desktop/image1.jpg'
file_name = 'image1.jpg'


# Custom MQTT message callback
def customCallback(client, userdata, message):
	print("Received a new message: ")
	print(message.payload)
	print("from topic: ")
	print(message.topic)
	print("--------------\n\n")
	
def lighttemperature():
    humidity, temperature = Adafruit_DHT.read_retry(11, temppin)
    print('Temp: {:.1f} C'.format(temperature))
    print('Humidity: {:.1f}'.format(humidity))
    return temperature
    
    
def displaytime(hour2,minutes2):
    hour_as_string = str(hour2)
    h1_as_string = str(minutes2)
    lcd.text(hour_as_string, 1)
    lcd.text(h1_as_string, 2)
    
    
host = "a3c16s480tb79n-ats.iot.us-east-1.amazonaws.com"
rootCAPath = "rootca.pem"
certificatePath = "certificate.pem.crt"
privateKeyPath = "private.pem.key"

my_rpi = AWSIoTMQTTClient("PubSub-p1812345")
my_rpi.configureEndpoint(host, 8883)
my_rpi.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

my_rpi.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
my_rpi.configureDrainingFrequency(2)  # Draining: 2 Hz
my_rpi.configureConnectDisconnectTimeout(10)  # 10 sec
my_rpi.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
my_rpi.connect()
my_rpi.subscribe("sensors/light", 1, customCallback)
my_rpi.subscribe("sensors/temperature", 1, customCallback)
sleep(2)

# Publish to the same topic in a loop forever
loopCount = 0
while True:
    now = datetime.datetime.now()
    hour = now.hour
    minute = now.minute
    h1 = hour/10
    h2 = hour % 10
    m1 = minute /10
    m2 = minute % 10
    
    displaytime(hour,minute)
    light = round(1024-(adc.value*1024))
    temperature2 = lighttemperature()
    
    
    message = {}
    message["deviceid"] = "deviceid_Alvin_pat"
    import datetime as datetime
    now = datetime.datetime.now()
    message["datetimeid"] = now.isoformat()      
    message["value"] = light
    import json
    my_rpi.publish("sensors/light", json.dumps(message), 1)
      
    message2 = {}
    message2["deviceid"] = "deviceid_Alvin_pat"
    now = datetime.datetime.now()
    message2["datetimeid"] = now.isoformat()      
    message2["value"] = temperature2
    my_rpi.publish("sensors/temperature", json.dumps(message2), 1)
    
sleep(5)
