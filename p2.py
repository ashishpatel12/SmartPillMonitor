#ASHISH PATEL
#SENIOR DESIGN
#Pill Box Python Script
import time
import boto3
import json
import time
import decimal
import datetime
import os
import pyttsx
import RPi.GPIO as GPIO
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

def checkTime(year,month,day,hour,minute):
    print('Starting checkTime function')
    print('Checking time: Year:{}, Month:{} Day: {}, Time: {}:{}'.format(year,month,day,hour,minute))
    print('---------------------------------')
    
    #Connect to DynamoDB
    dynamodb = boto3.resource("dynamodb", region_name='us-east-1',aws_access_key_id='',aws_secret_access_key='')
    table = dynamodb.Table('Pills')

    #Check Year
    year_response = table.scan(FilterExpression=Attr('Year').eq(year))
    year_items = year_response['Items']

    #Check Month
    month_response = table.scan(FilterExpression=Attr('Month').eq(month))
    month_items = month_response['Items']

    #Check Date
    day_response = table.scan(FilterExpression=Attr('Day').eq(day))
    day_items = day_response['Items']

    #Check Hour
    hour_response = table.scan(FilterExpression=Attr('Hour').eq(hour))
    hour_items = hour_response['Items']

    #Check Minute
    minute_response = table.scan(FilterExpression=Attr('Minute').eq(minute))
    minute_items = minute_response['Items']

    #LENGTH OF ISH
    year_response_len = len(year_items)
    month_response_len = len(month_items)
    day_response_len = len(day_items)
    hour_response_len = len(hour_items)
    minute_response_len = len(minute_items)

    if (year_response_len and month_response_len and day_response_len and hour_response_len and minute_response_len) != 0:
        response = table.scan(FilterExpression=Attr('Minute').eq(minute))
        Item = response['Items']

        for i in response[u'Items']:
            return(json.dumps(i,cls=DecimalEncoder))
    else:
        return 0

def checkPickup(pinCompartment):
    if pinCompartment == "A":
        pin = GPIO.input(40)
    elif pinCompartment == "B":
        pin = GPIO.input(38)
    elif pinCompoartment == "C":
        pin = GPIO.input(36)
    else:
        pin = 0
    
    timer = 0
    start = time.time()
    
    while timer == 0:
        stop = time.time()
        diff = stop - start
        if diff > 60:
            return 0
            timer = 1
        elif pin == 1:
            print 'the pin value is:'
            print pin
            return 1
            timer = 1
        

#GPIO SETUP
mode = GPIO.setmode(GPIO.BOARD)

GPIO.setup(36,GPIO.OUT)
GPIO.setup(38,GPIO.OUT)
GPIO.setup(40,GPIO.OUT)


x = 1

while x == 1:#Infinite While loop
    #Get Current Time
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute

    
    #Check Time Every minute to see if a pill should be taken 
    #pill_info = checkTime(year,month,day,hour,minute)
    
    #For Test
    #pill_info = checkTime(2018,4,28,23,38)
    pill_info = checkTime(now.year,now.month,now.day,now.hour,now.minute)
    

    if pill_info != 0:
        #String Formatter for Pill Information
        pill_info = pill_info.replace("{","")
        pill_info = pill_info.replace("}","")
        pill_info = pill_info.replace(":",",")
        #Convert to String
        info_list = pill_info.split(",")

        #Assign Values from String
        medication = info_list[1]
        compartment = info_list[11]
        
        #Speech Txt2Speech
        notif_text = 'It is time to take your'
        notif_text = notif_text + medication
        #os.system('espeak "{}"'.format(notif_text))
        #Add slot info and logic to tigger from here. This should 
        #the high/LOW from the Arduino of something has been taken
        print ('Take your {} that is in slot {}'.format(medication,compartment))
        
        pickup = checkPickup("A")
        
        if pickup == 1:
                print "Pill picked up"
        else:
            if pickup != 1:
                print "Alert Caregiver"


        print ('Take your {} that is in slot A'.format(medication)) 
        print pill_info

        
    
    
    time.sleep(60)

     
