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

