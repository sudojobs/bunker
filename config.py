#---------------------------------------
# Flow Meter & Relay Pins 
#---------------------------------------
flo=11  #FLOW  Sensor  GPIO PIN INPUT
sol=16  #RELAY CONTROL GPIO PIN OUTPUT
#---------------------------------------
# configure timeout/pertap and volume/tap
#---------------------------------------
tap_timeout = 30   #TIME OUT Seconds
tap_volume  = 142  #Pulses(100ml/142pulses)
#---------------------------------------
# System Configs  
#---------------------------------------
machine_id   ="03"
bypass_card  =1    #Default : 0
bypass_server=1    #Default : 0
#---------------------------------------
# maintenance  
#---------------------------------------
maintenance_id =[252525, 525252]
#---------------------------------------
# LCD ADDRESS 
#---------------------------------------
LCD_ADDRESS=0x27
#---------------------------------------
# LCD Messages 
#---------------------------------------
lcd_beer_name1    = "     Asahi $45      "
lcd_tout_message  = "     Time is up     "
lcd_pour_message  = "    Pour complete   "
lcd_ctap_message  = "  Please close tap  "
lcd_vout_message  = "    Enjoy Drink     "

lcd_strt_message = "   Please tap card  "
#lcd_strt_message  = "  Not in service   "
lcd_left_message  = "  Time left to pour "

lcd_left_blank_message   = "         "
lcd_right_blank_message  = "         "
lcd_count_blank_message  = "         "  

mmode_on                 ="Maintenance Mode ON "
mmode_off                ="Maintenance Mode OFF"
#---------------------------------------
# Log Messages
#---------------------------------------
log_name     = "BUNKER"
log_file     = 'app.log'
file_size    = 10000000
backup_count = 5
