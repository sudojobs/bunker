echo "Copy the Bunker Service....."
sudo cp bunker.service /lib/systemd/system/bunker.service
sudo chmod 644 /lib/systemd/system/bunker.service
sudo systemctl daemon-reload
sudo systemctl enable bunker.service
sudo reboot
