# fm-scanner
 #useful commands
 
 ### install python
 ```
 python3.7.4
 sudo apt-get update
 sudo apt-get install -y python3 git python3-pip
 sudo apt-get install python3-dev or  sudo apt-get install python3.9-dev  (version you have)
 ```
 ### create environment
 ```
 sudo pip install virtualenv (if sudo do not used virtualenv command will not be recognized)
 virtualenv --version
 virtualenv env
 source env/bin/activate
 deactivate
 ```
 
 ### requirements
 ```
 pip freeze > requirements.txt
 pip install -r requirements.txt
 
```

### adding directory to $PATH
```
echo $PATH
export PATH="/home/pi/.local/bin:$PATH"

```

### installing required python version - python3.7.4
```
sudo apt-get install -y build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev

wget https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tgz

sudo tar zxf Python-3.7.4.tgz
cd Python-3.7.4
sudo ./configure
sudo make -j 4
sudo make altinstall

which python

```

### create environment with specific python
```
virtualenv env --python=/usr/local/bin/python3.7  (can be seen in the directory)
```

### Installing pyaudio

```
sudo apt install portaudio19-dev
pip install PyAudio
```
### I2C enable
```
sudo raspi-config
```
interface options >>> enable I2C

### I2S driver install and enable

```
sudo apt-get -y update
sudo apt-get -y upgrade

cd ~
sudo pip3 install --upgrade adafruit-python-shell
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/i2smic.py
sudo python3 i2smic.py

arecord -l

```

### Linux-header version problem: Can't find build file
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get dist-upgrade
reboot
sudo apt-get install linux-headers-$(uname -r)

```

### Numpy libf77blas.so.3: cannot open shared file

```
sudo apt-get install libatlas-base-dev
```

# SYSTEMD starting scripts at reboot

create and edit new unit file
```
sudo nano /etc/systemd/system/example.service

```
Inside the unit file
```
[Unit]
Description=Example Service
Wants=network-online.target     //PartOf can be used too
After=network-online.target   //after device connected to a network start service

[Service]
Type=idle
Restart=on-failure
User=pi
ExecStart=/bin/bash -c 'cd /home/pi/examplePath && source env/bin/activate && python3 example.py'

[Install]
WantedBy=multi-user.target
```
Give permission to the file

```
sudo chmod 644 /etc/systemd/system/example.service
```
Update the daemon and enable service

```
sudo systemctl daemon-reload
sudo systemctl enable example.service
```
# Useful commands of SYSTEMD
```
sudo systemctl disable example.service
systemctl status example.service
```



