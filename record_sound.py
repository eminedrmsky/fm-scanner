import pyaudio
import socket
from _thread import start_new_thread
import sqlite3
from datetime import *
from pytz import timezone
#interrupt
import sys
import time
import RPi.GPIO as GPIO
import signal

#interrupt configuration

BUTTON_GPIO = 16 


def getTime():
    turkey = timezone('Europe/Istanbul')
    now = datetime.now(turkey)
    date =now.strftime("%Y.%m.%d %H:%M:%S")# name of .wav file
    return date

def signal_handler(sig,frame):
    GPIO.cleanup()
    print("exited")
    sys.exit(0)

def interrupt_handler(channel):

    date = getTime()
    try:
        con = sqlite3.connect("/home/pi/fm-scanner/fm-scanner/abe/get_status.db") 
        cursor = con.cursor()
    except Exception as e:
        print(e)

    if GPIO.input(BUTTON_GPIO):
        print("There is a power cut! Battery in use")
        cursor.execute("INSERT INTO power VALUES(?,?)",(date, "There is a power cut! Battery in use"))
        con.commit()
    else:
        print("Power came back! Battery is out")
        cursor.execute("INSERT INTO power VALUES(?,?)",(date, "Power came back! Battery is out"))
        con.commit() 


GPIO.setmode(GPIO.BCM)
    
GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)   
GPIO.add_event_detect(BUTTON_GPIO, GPIO.BOTH, 
        callback=interrupt_handler, bouncetime = 150)
    
signal.signal(signal.SIGINT, signal_handler)


############################################################################################################################################################

class soundStreaming():

    def __init__(self, audio):
        self.audio = audio

    def genHeader(self,sampleRate, bitsPerSample, channels):
        datasize = 2000*10**6
        o = bytes("RIFF",'ascii')                                               # (4byte) Marks file as RIFF
        o += (datasize + 36).to_bytes(4,'little')                               # (4byte) File size in bytes excluding this and RIFF marker
        o += bytes("WAVE",'ascii')                                              # (4byte) File type
        o += bytes("fmt ",'ascii')                                              # (4byte) Format Chunk Marker
        o += (16).to_bytes(4,'little')                                          # (4byte) Length of above format data
        o += (1).to_bytes(2,'little')                                           # (2byte) Format type (1 - PCM)
        o += (channels).to_bytes(2,'little')                                    # (2byte)
        o += (sampleRate).to_bytes(4,'little')                                  # (4byte)
        o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4,'little')  # (4byte)
        o += (channels * bitsPerSample // 8).to_bytes(2,'little')               # (2byte)
        o += (bitsPerSample).to_bytes(2,'little')                               # (2byte)
        o += bytes("data",'ascii')                                              # (4byte) Data Chunk Marker
        o += (datasize).to_bytes(4,'little')                                    # (4byte) Data size in bytes
        return o

    def find_device_index(self):
        audio = self.audio
        found = -1
        for i in range(audio.get_device_count()):
            dev = audio.get_device_info_by_index(i)
            name = dev['name'].encode('utf-8')
            print(i, name, dev['maxInputChannels'], dev['maxOutputChannels'])
            if name.lower().find(b'snd_rpi_i2s_card') >= 0 and dev['maxInputChannels'] > 0:
                found = i
                break
        if found < 0:
            print('No ReSpeaker USB device found')
        return found


def clientthread_record(port):
    while True:
        s =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(id(s))
        s.bind((socket.gethostname(),port))
        s.listen(5)
        clientsocket, address =s.accept()
        print("[-] Connected to " + address[0] + ":" + str(address[1]))
        print("connection established")
        first_run = True
        FLAG = True
        while FLAG:
            try:
                if first_run:            
                    data = wav_header + stream.read(CHUNK, exception_on_overflow = False)                
                    first_run = False
                    clientsocket.send(data)
                else:               
                    data = stream.read(CHUNK, exception_on_overflow = False)          
                    clientsocket.send(data)
            except Exception as e:
                print(e)
                s.close()
                first_run = True
                break


#############################################################################################################################################################################3

#tcp business

audio = pyaudio.PyAudio()
streaming = soundStreaming(audio)

sampleRate = 22050
bitsPerSample = 16
channels = 2

wav_header = streaming.genHeader(sampleRate, bitsPerSample, channels)


FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 4096   
device_index = streaming.find_device_index()

stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input= True,input_device_index=device_index,
                frames_per_buffer=CHUNK)  #sound device adjusted as input, sometimes raspberry sees it as output, write 'alsamixer' to
                #see more information or run device.py 

port_live = 1234
port_record = 1235

while True:
    s =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(id(s))
    s.bind((socket.gethostname(),port_live))
    s.listen(5)
    start_new_thread(clientthread_record, (port_record,))
    clientsocket, address =s.accept()
    print("[-] Connected to " + address[0] + ":" + str(address[1]))
    print("connection established")
    FLAG = True
    first_run = True
    while FLAG:
        try:
            if first_run:            
                data = wav_header + stream.read(CHUNK, exception_on_overflow = False)                
                first_run = False
                clientsocket.send(data)
            else:               
                data = stream.read(CHUNK, exception_on_overflow = False)          
                clientsocket.send(data)
        except Exception as e:
            print(e)
            s.close()
            first_run = True
            break 







