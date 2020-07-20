#!/usr/bin/env python
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
import glob
import logging
import logging.handlers


xml_file="temp.xml"
headers ={'Content-Type':'text/xml'}

sys_logger = logging.getLogger(cfg.log_name)
sys_logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.handlers.RotatingFileHandler(
              cfg.log_file, maxBytes=cfg.file_size, backupCount=cfg.backup_count)
handler.setFormatter(formatter)
sys_logger.addHandler(handler)

#---------------------------------------
#  Flow pulse Functions  
#---------------------------------------

def flowPulse(channel):
    global count
    global done
    if GPIO.input(cfg.flo):
       count = count + 1
       print(count)
       if count==cfg.tap_volume :        
          gpio_relay_off()
          done = 1

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(cfg.sol, GPIO.OUT)
GPIO.setup(cfg.flo,GPIO.IN)
GPIO.add_event_detect(cfg.flo, GPIO.RISING, callback=flowPulse)

#---------------------------------------
# Variable 
#---------------------------------------
global done
global count
count  = 0
done   = 0
state  = 0
maintenance_mode = 0 
#---------------------------------------
# GPIO Functions  
#---------------------------------------

def gpio_relay_off():
    print("----------------------------------------")
    print("System Info: Relay One OFF")
    print("----------------------------------------")
    sys_logger.info('Solenoid OFF')
    GPIO.output(cfg.sol,GPIO.HIGH)

def gpio_relay_on():
    print("----------------------------------------")
    print("System Info: Relay One ON")
    print("----------------------------------------")
    sys_logger.info('Solenoid ON')
    GPIO.output(cfg.sol,GPIO.LOW)

#---------------------------------------
#  Flow Meter Functions  
#---------------------------------------

def flow_meter(volume,seconds,mid):
    global totalMilliLitres
    global flowMilliLitres
    global count
    global done
    global state
    done             = 0
    totalMilliLitres = 0
    flowMilliLitres  = 0
    oldTime          = 0
    scount           = seconds 
    count            = 0
    start =time.time()
    time.clock()    
    elapsed = 0
    while True: 
          try:
              if ( done == 1 ):
                  sys_logger.info('%d ml dispensed (%d pulses)',int(count*.70425),count)
                  time.sleep(1)
                  lcd1.lcd_clear()
                  lcd1.lcd_display_string(cfg.lcd_pour_message, 2)
                  lcd1.lcd_display_string(cfg.lcd_ctap_message, 3)
                  done  = 0
                  time.sleep(1)
                  lcd_clear_local()
                  init_lcd_local()
                  break
              elif(elapsed < seconds):
                  elapsed = time.time() - start
                  value   = int((seconds) - (elapsed))
                  scount=scount-1
                  print(scount)
                  if(value < 0):
                      value =0
                  lcd1.lcd_clear()
                  lcd1.lcd_display_string("    Time Left: " + str(scount) , 2)  
                  time.sleep(1)
                  continue 
              else:
                  print ("Timeout of %02d Seconds" % (seconds))
                  gpio_relay_off() 
                  sys_logger.info('%d ml dispensed (%d pulses) ',int(count*.70425),count)
                  lcd1.lcd_clear()
                  sys_logger.info("%02d seconds Time Up" % (seconds))
                  lcd1.lcd_display_string(cfg.lcd_tout_message, 2)           
                  time.sleep(3)
                  print("now exiting")
                  state =0
                  break
          except KeyError:
                 print('The key you asked for is not here status has been set to False')
                 break
          

#---------------------------------------
#  XML Functions  
#---------------------------------------

def xml_file_create(mid,uid):
    print("----------------------------------------")
    print("System Info: XML file creation Started")
    print("----------------------------------------")
    sys_logger.info('XML file Creation Started')
    root = ET.Element("RequestMessage", ElementType="Memberverify")
    ET.SubElement(root, "MachineID").text = mid 
    ET.SubElement(root, "Cardno").text = uid 
    tree = ET.ElementTree(root)
    tree.write("temp.xml")
    sys_logger.info('XML file Creation Done')
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
    sys_logger.info('Server Authentication Start')
    with open(xml_file) as xml:
        # Give the object representing the XML file to requests.post.
        r = requests.post('http://128.129.2.168:1001/webole.asp', data=xml)
    print("----------------------------------------")
    print("System Info: Server Authentication Done")
    print("----------------------------------------")
    sys_logger.info('Server Authentication Done')
    content=ET.fromstring(r.content)
    
    status=content.find("Response/AnswerStatus")
    message=content.find("Response/Message")
    if status is not None:
       print("----------------------------------------")
       if status.text is not None: 
          print ("Server Info: Status  -> " + status.text)
          sys_logger.info('Stauts : %s', status.text)
    if message is not None:
       if message.text is not None: 
          print ("Server Info: Message -> " + message.text)
          sys_logger.info('Stauts : %s', message.text)
    print("----------------------------------------")

    if status is not None:
       return status.text,message.text
    else:
       return "Invalid","Contact Attendent"
	   
def init_lcd_local():
    lcd1.lcd_display_string(cfg.lcd_beer_name1, 1)
    lcd1.lcd_display_string(cfg.lcd_strt_message, 3)
	
def lcd_clear_local():
    lcd1.lcd_clear()

lcd1 = lcddriver.lcd(cfg.LCD_ADDRESS)

while True:
 try:
   if(state==0):
      if(maintenance_mode==0):
         lcd_clear_local()
      init_lcd_local()
      print("----------------------------------------")
      print("System Info: Please Tap Your Card"       )
      print("----------------------------------------")
      tcflush(sys.stdin, TCIFLUSH)
      if(cfg.bypass_card==0):
         card=raw_input()
      else:
         print("Press Return...")
         raw_input()
         card="02-00300-32875"
         time.sleep(2)
         print("----------------------------------------")
         print( "Card Bypassed : " + card )
         print("----------------------------------------")
         sys_logger.info('Card Mode Bypass')
      sys_logger.info('Card No : %s' ,card)
      user_id    = card[9:]
      tcflush(sys.stdin, TCIFLUSH)
      print("----------------------------------------")
      print( "System Info: Machine ID : " + str(cfg.machine_id) )
      print("System Info: User ID : " + user_id        )
      print("----------------------------------------")
      if user_id in cfg.maintenance_id:
          state=3    
          continue
      else:
          if(cfg.bypass_server==0):
             xml_file_create(cfg.machine_id,user_id)
             status,msg=auth_from_server()
             xml_file_delete()
          else:
             status="OK"
             print("----------------------------------------")
             print( "Server Bypassed Status : " + status )
             print("----------------------------------------")
          status_message = cfg.lcd_left_blank_message + status + cfg.lcd_right_blank_message
          print(status_message)
          if(status=="OK"):
             state=1
          elif(status=="DM"):
             state=2
          else:
             state=4
          continue
   elif(state==1):
      lcd1.lcd_clear()
      lcd1.lcd_display_string(status_message, 2)
      time.sleep(1)
      gpio_relay_on()
      flow_meter(cfg.tap_volume,cfg.tap_timeout,cfg.machine_id)
      state=0
      sys_logger.info('Dispense done')
      continue
   elif(state==2):       
      lcd1.lcd_clear()
      lcd1.lcd_display_string(status, 2)
      lcd1.lcd_display_string(msg, 3)
      time.sleep(3)
      lcd1.lcd_clear()
      lcd1.lcd_display_string(lcd_strt_message, 2)
      print("========================================")
      print("System Info : " + msg                    )
      print("========================================")
      sys_logger.error('%s',msg)
      state=0
      continue
   elif(state==3):
      if(maintenance_mode==0):
         count=0
         lcd1.lcd_clear()
         lcd1.lcd_display_string(cfg.mmode_on, 4)
         gpio_relay_on()
         print("========================================")
         print("Maintenance Mode ON")
         print("========================================")
         sys_logger.info('Maintenance Mode ON')
         time.sleep(3)
         maintenance_mode=1
         state=0
         continue 
      else:
         lcd1.lcd_clear()
         lcd1.lcd_display_string(cfg.mmode_off, 4)
         gpio_relay_off()
         print("========================================")
         print("Maintenance Mode OFF")
         print("%d ml dispensed (%d pulses)" % (int(count*.70425),count))
         print("========================================")
         sys_logger.info('Maintenance Mode OFF')
         sys_logger.info('%d ml dispensed (%d pulses)' , int(count*.70425),count)
         time.sleep(3)
         maintenance_mode=0
         count=0
         state=0
         continue 
   else:
       lcd1.lcd_clear()
       lcd1.lcd_display_string(status, 2)
       lcd1.lcd_display_string(msg, 3)
       time.sleep(3)
       lcd1.lcd_clear()
       lcd1.lcd_display_string(cfg.lcd_strt_message, 2)                
       print("========================================")
       print("System Info : " + status + "  " + msg    )
       print("========================================")
       sys_logger.error('%s : %s',status,msg)
       state=0
       continue

 except KeyboardInterrupt:
       print('You cancelled the operation.')
       sys_logger.error('System Exit')
       GPIO.cleanup()
       sys.exit(0)

 except KeyError:
     print('The key you asked for is not here status has been set to False')
