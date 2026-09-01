Flash the RPI Zero W with with Raspberry Pi OS Lite 32bit
Hostname: pumpkin
Username: pi
Password: ******
Wi-Fi: ******
Wi-Fi country: Australia
Locale/timezone: Australia/Brisbane
Enable SSH: Yes

Update and upgrade packages:
sudo apt update
sudo apt full-upgrade -y

Enable I2C communication:
sudo raspi-config
Interface Options -> I2C -> Enable

Install python, pip, git, i2c tools and smbus:
sudo apt install -y python3 python3-pip python3-venv git i2c-tools python3-smbus

Clone the repository:
cd ~
git clone https://github.com/Jiayisaac/Pumpkin.git
cd Pumpkin

Install and activate python venv:
python3 -m venv --system-site-packages venv
source venv/bin/activate

Install requirements
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

Test app works:
python3 app.py

Add pumpkin.service to:
/etc/systemd/system/pumpkin.service

Start the service:
sudo systemctl daemon-reload
sudo systemctl enable pumpkin.service
sudo systemctl start pumpkin.service

Check the service is running:
sudo systemctl status pumpkin.service