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
from gtts import gTTS
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from twilio.rest import Client


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
    #dynamodb = boto3.resource("dynamodb", region_name='us-east-1',aws_access_key_id='AKIAI2ZWMFGK662RHKNA',aws_secret_access_key='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')
    
    dynamodb = boto3.resource("dynamodb", region_name='us-east-1',aws_access_key_id=[insert aws key],aws_secret_access_key=[insert secret key])
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


def textmessage(text):
    account_sid = 'ACea1e5fd7f947294b7656d8036d95c79e'
    auth_token = 'fc43c469e99fcacb0646e7f0c6b1d1e1'
    client = Client(account_sid, auth_token)

    message = client.messages.create(
                                body = text,
                                from_= '+12678438414',
                                to = '+19083914086'
                                                                                        )
    print(message,account_sid)


def checkPickup(compartment):
    import time
    #SET GPIO MODE TO BOARD PORTS
    mode = GPIO.setmode(GPIO.BOARD)

    #SET GPIO WARNINGS TO FALSE
    GPIO.setwarnings(False)

    GPIO.setup(40,GPIO.OUT)
    GPIO.setup(38,GPIO.OUT)
    GPIO.setup(36,GPIO.OUT)

    #CHECK WHAT COMPARTMENT IS NEEDED TO CHECK
    if (compartment == "A"):
        pin = GPIO.input(40)
        print 'Compartment Assigned: A'
    elif (compartment == "B"):
        pin = GPIO.input(38)
        print 'Compartment Assigned: B'
    elif (compartment == "C"):
        pin = GPIO.input(36)
        print 'Compartment Assigned: C'
    else:
        print 'READ ISSUE BRO'

    timer = 0
    start = time.time()
    pin = 0


    #IF 5-minutes without pickup repead
    #IF 5 more minutes => ALERT CAREGIVER
    #IF Pill Picked up checkPickup function
    while timer == 0:
        stop = time.time()
        diff = stop - start
        #Time between notifications (in seconds)
        if diff > 10:
            print 'TIME EXPIRED'
            time = 1
            return 0
        
        elif (compartment == "A"):
            pin = GPIO.input(40)
            if (pin == 1):
                print '================='
                print 'PILL PICKED UP: A'
                print '================='
                timer = 1
                return 1

        elif (compartment == "B"):
            pin = GPIO.input(38)
            if (pin == 1):
                print '================='
                print 'PILL PICKED UP: B'
                print '================='
                timer = 1
                return 1
        elif (compartment == "C"):
            pin = GPIO.input(36)
            if pin == 1:
                print '================='
                print 'PILL PICKED UP:C'
                print '================='
                timer = 1
                return 1

    GPIO.cleanup()
        



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
        compartment = compartment.replace(" ","")
        compartment = compartment.replace('"','')
        #compartment = compartment.replace('"',"")        
        #Speech Txt2Speech
        notif_text = 'It is time to take your'
        notif_text_2 = " in slot "
        notif_text = notif_text + medication + notif_text_2 + compartment
        #os.system('espeak "{}"'.format(notif_text))
        #Add slot info and logic to tigger from here. This should 
        #the high/LOW from the Arduino of something has been taken
        print ('Take your {} that is in slot {}'.format(medication,compartment))
        
        #gTTS Text-to-Speech Library
        tts = gTTS(text=notif_text, lang='en', slow=False)
        #Create Text-to-Speech MP3 file
        tts.save("pill_notif.mp3")
        os.system("mpg321 pill_notif.mp3")
        
        #os.system('espeak "{}"'.format(notif_text))
        pickup = checkPickup(compartment)
       
        #DEBUGGIN VARIABLE PRINT
        #print "pickup function complete"

        if pickup == 1:
                print "Pill picked up, EXIT FUNCTION"
        else:
            if pickup != 1:
                os.system("mpg321 pill_notif.mp3")
                #os.system('espeak "{}"'.format(notif_text))
                pickup2 = checkPickup(compartment)
                if pickup2 != 1:
                    os.system("mpg321 pill_notif.mp3")
                    #os.system('espeak "{}"'.format(notif_text))
                    textmessage(notif_text)
                    print "Alert Caregiver, Pill has not been picked up"

        print ('Take your {} that is in slot {}'.format(medication, compartment)) 
        print pill_info    
    
    time.sleep(20)

     
