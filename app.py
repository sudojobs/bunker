import os
import xml.etree.ElementTree as ET
import RPi.GPIO as GPIO
import requests
import lcddriver
import config as cfg
import time
import sys
from   termios import tcflush, TCIFLUSH
from   time import *

xml_file="temp.xml"
headers ={'Content-Type':'text/xml'}

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(cfg.sol, GPIO.OUT)
GPIO.setup(cfg.flo,GPIO.IN)
GPIO.add_event_detect(cfg.flo, GPIO.RISING, callback=flowPulse)

#---------------------------------------
# Variable 
#---------------------------------------
global done
global count
count            = 0
done             = 0

#---------------------------------------
# GPIO Functions  
#---------------------------------------

def gpio_relay_on():
    print("----------------------------------------")
    print("System Info: Relay One ON")
    print("----------------------------------------")
    GPIO.output(cfg.sol,HIGH)

def gpio_relay_off():
    print("----------------------------------------")
    print("System Info: Relay One OFF")
    print("----------------------------------------")
    GPIO.output(cfg.sol,LOW)

#---------------------------------------
#  Flow Meter Functions  
#---------------------------------------

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
                  print("volumeout !!!")
                  lcd1.lcd_clear()
                  lcd1.lcd_display_string(cfg.lcd_pour_message, 2)
                  lcd1.lcd_display_string(cfg.lcd_ctap_message, 3)
                  done  = 0
                  time.sleep(3)
                  lcd_clear_local()
                  init_lcd_local()
              elif(elapsed < seconds):
                  elapsed = int(round(time.time()) - round(start))
                  value   = int(seconds - elapsed)
                  time.sleep(0.1)
                  lcd1.lcd_clear()
                  time.sleep(0.1)
                  lcd1.lcd_display_string("    Time Left: " + str(value) , 2)                       
                  time.sleep(1)
              else:
                  print ("Timeout of %02d Seconds" % (seconds))
                  lcd1.lcd_clear()
                  lcd1.lcd_display_string(cfg.lcd_tout_message, 2)           
                  print("now exiting")
          except KeyError:
                 print('The key you asked for is not here status has been set to False')
                 break
          
#---------------------------------------
#  Flow pulse Functions  
#---------------------------------------

def flowPulse(channel):
    if GPIO.input(7):
       global count
       global done
       count = count + 1
       print(count)
       if count==cfg.tap_volume :        
          done = 1
          gpio_relay_off()

#---------------------------------------
#  XML Functions  
#---------------------------------------

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
    lcd1.lcd_display_string(cfg.lcd_strt_message, 2)
	
def lcd_clear_local():
    lcd1.lcd_clear()

lcd1 = lcddriver.lcd(cfg.LCE_ADDRESS)
init_lcd_local()

while True:
 try:
   if(state==0):
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
         state=1
      elif(status=="DM"):
         state=2
      else
         state=3
      continue
   elif(state==1):
      lcd1.lcd_clear()
      lcd1.lcd_display_string(status_message, 2)
      time.sleep(1)
      gpio_relay_on()
      flow_meter(cfg.tap_volume,cfg.tap_timeout,machine_id)
      gpio_relay_off()
      state=0
      continue
   elif(state==2):       
      lcd1.lcd_clear()
      lcd1.lcd_display_string(status, 2)
      lcd1.lcd_display_string(msg, 3)
      time.sleep(3)
      lcd1.lcd_clear()
      lcd1.lcd_display_string(lcd_strt_message, 2)
      print("========================================")
      print "System Info : " + msg
      print("========================================")
      state=0
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
       state=0
       continue

 except KeyboardInterrupt:
       print('You cancelled the operation.')
       GPIO.cleanup()
       sys.exit(0)

 except KeyError:
     print('The key you asked for is not here status has been set to False')
