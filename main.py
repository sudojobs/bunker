import os
import xml.etree.ElementTree as ET
import RPi.GPIO as GPIO
import requests
import lcddriver
import config as cfg
from time import *
import time
import sys
from termios import tcflush, TCIFLUSH

#lcd_strt_message  = "   Please tap card  "
lcd_strt_message  = "   Not in service   "
lcd_left_message  = "  Time left to pour "


xml_file="temp.xml"
headers ={'Content-Type':'text/xml'}
flag = 0
timeout = 5
# setting a current mode
GPIO.setmode(GPIO.BCM)
#removing the warings 
GPIO.setwarnings(False)
#creating a list (array) with the number of GPIO's that we use 
pins =  24
flow1 = 7
#---------------------------------------
# 20x4 LCD ADDRESS
#---------------------------------------
ADDRESS1=0x27

#setting the mode for all pins so all will be switched on 
GPIO.setup(pins, GPIO.OUT)

global done
global count
global totalMilliLitres
global flowMilliLitres  
totalMilliLitres =0 
count = 0
flowMilliLitres = 0
oldTime = 0
calibrationFactor = 4.5
done = 0


def gpio_relay_off():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(24,GPIO.OUT)
    GPIO.output(24,0)

def flow_meter(volume,seconds,mid):
    global oldTime
    global totalMilliLitres
    global flowMilliLitres
    global count
    global done
    done             = 0
    totalMilliLitres = 0
    flowMilliLitres  = 0
    oldTime          = 0
    count            = 0
    flowRate         = 0
    start = time.time()
    time.clock()    
    elapsed = 0
    while True: 
          try:
              if ( done == 1 ):
                  GPIO.cleanup()
                  time.sleep(3)
                  print "volumeout !!!"
                  lcd1.lcd_clear()
                  lcd1.lcd_display_string(cfg.lcd_pour_message, 2)
                  lcd1.lcd_display_string(cfg.lcd_ctap_message, 3)
                  done  = 0
                  flag  = 1
                  time.sleep(3)
                  lcd_clear_local()
                  init_lcd_local()
                  sys.exit(0)
              elif(elapsed < seconds):
                  #print done
                  elapsed = int(round(time.time()) - round(start))
                  #print "Timeout Elapsed Seconds: %02d" % ( seconds - elapsed)
                  value   = int(seconds - elapsed)
                  #print round(time.time(),0)
                  #print round(start,0)           
                  #print elapsed
                  #value   = seconds - int(elapsed)
                  #print value
                  #values  = "         " + str(value) + "         " 
                  time.sleep(0.1)
                  lcd1.lcd_clear()
                  time.sleep(0.1)
                   #    lcd1.lcd_display_string(lcd_left_message, 2)
                  lcd1.lcd_display_string("    Time Left: " + str(value) , 2)                       
                  time.sleep(1)
              else:
                  gpio_relay_off()
                  GPIO.cleanup()           
                  print "Timeout of %02d Seconds" % (seconds)
                  lcd1.lcd_clear()
                  lcd1.lcd_display_string(cfg.lcd_tout_message, 2)           
                  totalMilliLitres = 0
                  flowMilliLitres  = 0
                  oldTime          = 0
                  count            = 0
                  flowRate         = 0
                  print("now exiting")
                  sys.exit(1)
          except KeyError:
                 print('The key you asked for is not here status has been set to False')
                 break
          
def countPulse1(channel):
    if GPIO.input(7):
       global count
       global done
       count = count + 1
       print(count)
       if count==cfg.tap1volume :        
	  time.sleep(1)
          done = 1
          gpio_relay_off()
          sys.exit(0) 
          


def xml_file_create(mid,uid):
    print("----------------------------------------")
    print("System Info: XML file creation Started")
    print("----------------------------------------")
    root = ET.Element("RequestMessage", ElementType="Memberverify")
    ET.SubElement(root, "MachineID").text = mid 
    ET.SubElement(root, "Cardno").text = uid 
    tree = ET.ElementTree(root)
    tree.write("temp.xml")
    print("----------------------------------------")
    print("System Info: XML file creation Done")
    print("----------------------------------------")

def xml_file_delete():
    print("----------------------------------------")
    print("System Info: XML file Deleted")
    print("----------------------------------------")
    #os.remove("temp.xml")

def auth_from_server():
    print("----------------------------------------")
    print("System Info: Server Authentication Start")
    print("----------------------------------------")
    with open(xml_file) as xml:
        # Give the object representing the XML file to requests.post.
        r = requests.post('http://128.129.2.170:5001/webole.asp', data=xml)
    print("----------------------------------------")
    print("System Info: Server Authentication Done")
    print("----------------------------------------")
    content=ET.fromstring(r.content)
    
    status=content.find("Response/AnswerStatus")
    message=content.find("Response/Message")
    if status is not None:
       print("----------------------------------------")
       if status.text is not None: 
          print "Server Info: Status  -> " + status.text
    if message is not None:
       if message.text is not None: 
          print "Server Info: Message -> " + message.text
    print("----------------------------------------")

    if status is not None:
       return status.text,message.text
    else:
       return "Invalid","Contact Attendent"
	   
	   
def init_lcd_local():
    lcd1.lcd_display_string(cfg.lcd_beer_name1, 1)
    lcd1.lcd_display_string(lcd_strt_message, 2)
	
def lcd_clear_local():
    lcd1.lcd_clear()

GPIO.cleanup()

gpio_relay_off()

lcd1 = lcddriver.lcd(ADDRESS1)
init_lcd_local()

while True:
 try:
   print("----------------------------------------")
   print("System Info: Please Tap Your Card")
   print("----------------------------------------")
   tcflush(sys.stdin, TCIFLUSH)
   card=raw_input()
   #card="01-00300-11984"
   user_id    = card[9:]
   tcflush(sys.stdin, TCIFLUSH)
   print("----------------------------------------")
   print "System Info: Machine ID : " + machine_id
   print "System Info: User ID : " + user_id
   print("----------------------------------------")
   xml_file_create(machine_id,user_id)
   status,msg=auth_from_server()
   xml_file_delete()
   status_message = cfg.lcd_left_blank_message + status + cfg.lcd_right_blank_message
   if(status=="OK"):
         lcd1.lcd_clear()
         lcd1.lcd_display_string(status_message, 2)
         #lcd1.lcd_display_string(msg, 3)
         time.sleep(1)
         print("----------------------------------------")
         print("System Info: Relay One ON")
         print("----------------------------------------")
         GPIO.setmode(GPIO.BCM)
         GPIO.setup(24,GPIO.OUT)
         GPIO.setup(flow1,GPIO.IN)
         GPIO.output(24,GPIO.HIGH)
         GPIO.add_event_detect(flow1, GPIO.RISING, callback=countPulse1, bouncetime=300)
         flow_meter(cfg.tap1volume,cfg.tap1timeout,machine_id)
         print("----------------------------------------")
         print("System Info: Relay One OFF")
         print("----------------------------------------")
   elif(status=="DN"):       
        lcd1.lcd_clear()
        lcd1.lcd_display_string(status, 2)
        lcd1.lcd_display_string(msg, 3)
        time.sleep(3)
        lcd1.lcd_clear()
        lcd1.lcd_display_string(lcd_strt_message, 2)
        print("========================================")
        print "System Info : " + msg
        print("========================================")
        continue
   else:
       lcd1.lcd_clear()
       lcd1.lcd_display_string(status, 2)
       lcd1.lcd_display_string(msg, 3)
       time.sleep(3)
       lcd1.lcd_clear()
       lcd1.lcd_display_string(lcd_strt_message, 2)                
       print("========================================")
       print "System Info : " + status + "  " + msg
       print("========================================")
       continue

 except KeyboardInterrupt:
       print('You cancelled the operation.')
       GPIO.cleanup()
       sys.exit(0)

 except KeyError:
     #status = False
     print('The key you asked for is not here status has been set to False')
