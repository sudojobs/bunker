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
import logging

xml_file="temp.xml"
headers ={'Content-Type':'text/xml'}
logging.basicConfig(filename='app.log', filemode='w',format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

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
machine_id = 0
#---------------------------------------
# GPIO Functions  
#---------------------------------------

def gpio_relay_off():
    print("----------------------------------------")
    print("System Info: Relay One OFF")
    print("----------------------------------------")
    logging.info('Solenoid OFF')
    GPIO.output(cfg.sol,GPIO.HIGH)

def gpio_relay_on():
    print("----------------------------------------")
    print("System Info: Relay One ON")
    print("----------------------------------------")
    logging.info('Solenoid ON')
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
    count            = 0
    start =time.time()
    time.clock()    
    elapsed = 0
    while True: 
          try:
              if ( done == 1 ):
                  ml=cfg.tap_volume/1.42
                  logging.info('%d ml dispensed (%d pulses)',ml,cfg.tap_volume)
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
                  elapsed = int((time.time()) - (start))
                  value   = int(seconds) - int(elapsed)
                  print(value)
                  if(value < 0):
                      value =0
                  #time.sleep(0.1)
                  lcd1.lcd_clear()
                  #time.sleep(0.1)
                  lcd1.lcd_display_string("    Time Left: " + str(value) , 2)                       
                  time.sleep(1)
                  continue 
              else:
                  print ("Timeout of %02d Seconds" % (seconds))
                  gpio_relay_off() 
                  logging.error('%02d Timeout ',seconds)
                  lcd1.lcd_clear()
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
    logging.info('XML file Creation Started')
    root = ET.Element("RequestMessage", ElementType="Memberverify")
    ET.SubElement(root, "MachineID").text = mid 
    ET.SubElement(root, "Cardno").text = uid 
    tree = ET.ElementTree(root)
    tree.write("temp.xml")
    logging.info('XML file Creation Done')
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
    logging.info('Server Authentication Start')
    with open(xml_file) as xml:
        # Give the object representing the XML file to requests.post.
        r = requests.post('http://128.129.2.170:5001/webole.asp', data=xml)
    print("----------------------------------------")
    print("System Info: Server Authentication Done")
    print("----------------------------------------")
    logging.info('Server Authentication Done')
    content=ET.fromstring(r.content)
    
    status=content.find("Response/AnswerStatus")
    message=content.find("Response/Message")
    if status is not None:
       print("----------------------------------------")
       if status.text is not None: 
          print ("Server Info: Status  -> " + status.text)
          logging.info('Stauts : %s', status.txt)
    if message is not None:
       if message.text is not None: 
          print ("Server Info: Message -> " + message.text)
          logging.info('Stauts : %s', message.txt)
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

def manage_log_file():
    print("Manage_Log_file")
#    #check_file_size;
#    if more than 10MB :
#        #check number of files:
#            if it is more than 10:
#                delete the last one:
#                rename logfile logfile.date.time
#                create new logfile
#            else
#                rename logfile logfile.data.time
#                create new logfile


lcd1 = lcddriver.lcd(cfg.LCD_ADDRESS)

while True:
 try:
   if(state==0):
      lcd_clear_local()
      init_lcd_local()
      print("----------------------------------------")
      print("System Info: Please Tap Your Card"       )
      print("----------------------------------------")
      tcflush(sys.stdin, TCIFLUSH)
      card=raw_input()
      #card="01-00300-11984"
      logging.info('Card No : %s' ,card)
      user_id    = card[9:]
      tcflush(sys.stdin, TCIFLUSH)
      machine_id="03"
      print("----------------------------------------")
      print( "System Info: Machine ID : " + machine_id )
      print("System Info: User ID : " + user_id        )
      print("----------------------------------------")
      #xml_file_create(machine_id,user_id)
      #status,msg=auth_from_server()
      #xml_file_delete()
      status="OK"
      status_message = cfg.lcd_left_blank_message + status + cfg.lcd_right_blank_message
      print(status_message)
      if(status=="OK"):
         state=1
      elif(status=="DM"):
         state=2
      else:
         state=3
      continue
   elif(state==1):
      lcd1.lcd_clear()
      lcd1.lcd_display_string(status_message, 2)
      time.sleep(1)
      gpio_relay_on()
      flow_meter(cfg.tap_volume,cfg.tap_timeout,machine_id)
      #gpio_relay_off()
      state=0
      logging.info('Dispense done')
      manage_log_file()
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
      logging.error('%s',msg)
      state=0
      manage_log_file()
      continue
   else:
       lcd1.lcd_clear()
       lcd1.lcd_display_string(status, 2)
       lcd1.lcd_display_string(msg, 3)
       time.sleep(3)
       lcd1.lcd_clear()
       lcd1.lcd_display_string(lcd_strt_message, 2)                
       print("========================================")
       print("System Info : " + status + "  " + msg    )
       print("========================================")
       logging.error('%s : %s',status,msg)
       state=0
       manage_log_file()
       continue

 except KeyboardInterrupt:
       print('You cancelled the operation.')
       logging.error('System Exit')
       GPIO.cleanup()
       sys.exit(0)

 except KeyError:
     print('The key you asked for is not here status has been set to False')
