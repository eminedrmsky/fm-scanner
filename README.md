# fm-scanner
 #useful commands
 
 ### install python
 ```
 python3.6.8
 sudo apt-get install -y python3 git python3-pip
 sudo apt-get install python3-dev or  sudo apt-get install python3.9-dev  (version you have)
 ```
 ### create environment
 ```
 pip install virtualenv
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
virtualenv env --python=/usr/local/bin/python3.7.4
```

### Installing pyaudio

```
sudo apt install portaudio19-dev
pip install PyAudio
```

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



