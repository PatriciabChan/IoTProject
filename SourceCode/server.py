
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from flask import Flask, render_template, jsonify, request,Response
from gpiozero import Motor, Buzzer, LED, InputDevice, Button, MCP3008
from rpi_lcd import LCD
from time import sleep
import mysql.connector
import sys

import json
import numpy
import datetime
import decimal

import gevent
import gevent.monkey
from gevent.pywsgi import WSGIServer
from picamera import PiCamera
import time, datetime
import boto3
import botocore

s3 = boto3.resource('s3')
from rpi_lcd import LCD

app = Flask(__name__)

import dynamodb
import dynamodbfanlog
import dynamodbtemperature
import jsonconverter as jsonc

# Custom MQTT message callback
def customCallback(client, userdata, message):
	print("Received a new message: ")
	print(message.payload)
	print("from topic: ")
	print(message.topic)
	print("--------------\n\n")

lcd = LCD()
motor2 = Motor(20,22, pwm = True)

full_path = '/home/pi/Desktop/image1.jpg'
file_name = 'image1.jpg'

host = "a3c16s480tb79n-ats.iot.us-east-1.amazonaws.com"
rootCAPath = "rootca.pem"
certificatePath = "certificate.pem.crt"
privateKeyPath = "private.pem.key"

BUCKET = 'sp-p1650688-s3-bucket' # replace with your own unique bucket name
location = {'LocationConstraint': 'us-east-1'}
file_path = "/home/pi/Desktop"
file_name = "test.jpg"
best_bet_item = "Unknown"


my_rpi = AWSIoTMQTTClient("PubSub-p1650688")
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

def takepicture():
        takePhoto(file_path, file_name)
        bucket = 'sp-p1650688-s3-bucket' # replace with your own unique bucket name
        exists = True
        s3.meta.client.head_bucket(Bucket=bucket)
        s3.Object(bucket, file_name).put(Body=open(full_path, 'rb'))
        print("File uploaded")

def takePhoto(file_path,file_name):
    with PiCamera() as camera:
        #camera.resolution = (1024, 768)
        full_path = file_path + "/" + file_name
        camera.capture(full_path)
        sleep(3)


            


@app.route("/takepicture/picture")
def takepictureroute():
    takepicture()
    print"test"
    return 'ok'

global currentfanspeed
@app.route("/writeMotor0/motoroff")
def fanoff():
    currentfanspeed = 0
    motor2.stop()
    uploadfanstatus("Fan Speed: " + str(currentfanspeed))
    return'ok'
@app.route("/writeMotor1/motorspeed1")
def fanspeed1():
    motor2.backward(speed=0.25)
    currentfanspeed = 1
    uploadfanstatus("Fan Speed: " +str(currentfanspeed))
    return'ok'
@app.route("/writeMotor2/motorspeed2")
def fanspeed2():
    motor2.backward(speed=0.50)
    currentfanspeed = 2
    uploadfanstatus("Fan Speed: " +  str(currentfanspeed))
    return'ok'
@app.route("/writeMotor3/motorspeed3")
def fanspeed3():
    motor2.backward(speed=0.75)
    currentfanspeed = 3
    uploadfanstatus("Fan Speed: " + str(currentfanspeed))
    return'ok'
@app.route("/writeMotor4/motorspeed4")
def fanspeed4():
    motor2.backward(speed=1)
    currentfanspeed = 4
    uploadfanstatus("Fan Speed: " + str(currentfanspeed))
    return'ok'
@app.route("/writeMotor5/motorauto")
def fanspeedauto():
    print("test")

def uploadfanstatus(speedvalue):
    message = {}
    message["deviceid"] = "deviceid_Alvin_pat"
    import datetime as datetime
    now = datetime.datetime.now()
    message["datetimeid"] = now.isoformat()      
    message["value"] = speedvalue
    import json
    my_rpi.publish("fan/fanspeed", json.dumps(message), 1)

@app.route("/api/getdata",methods=['POST','GET'])
def apidata_getdata():
    if request.method == 'POST' or request.method == 'GET':
        try:
            data = {'chart_data': jsonc.data_to_json(dynamodb.get_data_from_dynamodb()), 
             'title': "IOT Data"}
            return jsonify(data)

        except:
            import sys
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])

@app.route("/api/getfandata",methods=['POST','GET'])
def apidata_getfandata():
    if request.method == 'POST' or request.method == 'GET':
        try:
            data = {'chart_data': jsonc.data_to_json(dynamodbfanlog.get_data_from_dynamodb()), 
             'title': "Fan Logs"}
            return jsonify(data)

        except:
            import sys
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])        

@app.route("/api/gettemperature",methods=['POST','GET'])
def apidata_gettemperature():
    if request.method == 'POST' or request.method == 'GET':
        try:
            data = {'chart_data': jsonc.data_to_json(dynamodbtemperature.get_data_from_dynamodb()), 
             'title': "temperate Logs"}
            return jsonify(data)

        except:
            import sys
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])


@app.route("/")
def home():
    return render_template("index.html")
    

        
    
app.run(debug=True,host="0.0.0.0")
