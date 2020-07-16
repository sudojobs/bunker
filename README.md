Bunker System 
(it is solenoid flowmeter based touchless beer dispensing system)

-- To Run the System
   
   cd bunker
   python app.py

-- To Install as Service (On boot)
   ./install.sh
   (this require Reboot)

-- To Check the Status of Service
   sudo systemctl status bunker.service
   
-- To Check the Stop of Service
   sudo systemctl stop bunker.service

-- To Check the Start of Service
   sudo systemctl start bunker.service

-- To Check the Restart of Service
   sudo systemctl start bunker.service
