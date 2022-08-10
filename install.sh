echo "installing the essentials"
sudo apt-get update
sudo apt-get -y install vim-gtk
echo "install the xterm"
sudo sudo apt-get install xterm -y
echo "Copy the Bunker Service.....to bootmode"
mkdir /home/pi/.config/autostart
sudo cp app.desktop /home/pi/.config/autostart
echo "copy config.txt"
sudo cp /boot/config.txt confit.txt.org
diff config.txt config.txt.org | more
sudo cp config.txt /boot/config.txt
echo "Reboot the System"
sudo reboot
