echo "installing the essentials"
sudo apt-get -y install vim-gtk
echo "install the guizero"
sudo pip install guizero
echo "Copy the Bunker Service.....to bootmode"
sudo cp app.desktop /etc/xdg/autostart/app.desktop
echo "copy config.txt"
sudo cp /boot/config.txt confit.txt.org
diff config.txt config.txt.org | more
sudo cp config.txt /boot/config.txt
echo "Reboot the System"
sudo reboot
