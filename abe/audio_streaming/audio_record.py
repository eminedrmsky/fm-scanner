#Does the sound recording process of Module_0. It is called in main.py, module_0 function.############################################
import shutil
import pyaudio
import wave
from datetime import *
import os
from pytz import timezone
import sqlite3
import numpy as np
import socket
from time import sleep

try:
    # TCP server
    s =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((socket.gethostname(),1234))

    # Database connection
    con = sqlite3.connect("/home/pi/fm-scanner/fm-scanner/abe/get_status.db") 
    cursor = con.cursor()

    audio = pyaudio.PyAudio() # create pyaudio instantiation

except Exception as e:
    print(e)

#######################################################################################################################################################################3

class databaseBusiness():

    def __init__ (self, con,cursor):
        self.con = con
        self.cursor = cursor

    def getNumberOfFrequencies(self):
        con = self.con
        cursor = self.cursor
        rowsQuery = "SELECT Count(*) FROM status"
        cursor.execute(rowsQuery)
        NumberofChannels =  cursor.fetchone()[0]
        return NumberofChannels
    
    def writeRecords(self):
        con = self.con
        cursor = self.cursor
        cursor.execute("SELECT freq,stat FROM status")
        data = cursor.fetchall() 
        info=[(str(i[0]) + "Hz:" + i[1] + ", " ) for i in data]
        info_str = " "
        info_str = info_str.join(info)
        cursor.execute("INSERT INTO records VALUES(?,?,?)",(wav_output_filename, record_secs, info_str))
        con.commit()
    
    def recording_process(self):
        crsr = self.cursor
        crsr.execute("SELECT stat FROM dinleme WHERE var = 'record'") 
        data = crsr.fetchall()
        return data[0][0]


def newest(path):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files if basename.endswith('.wav')]
    return max(paths, key=os.path.getctime)  

def oldest(path):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files if basename.endswith('.wav')]
    return min(paths, key=os.path.getctime)  


class audioRecording():

    def __init__ (self, s):
        self.s = s
        
    def getTime(self):
        turkey = timezone('Europe/Istanbul')
        now = datetime.now(turkey)
        wav_output_filename =now.strftime("%Y.%m.%d %H:%M:%S")# name of .wav file
        return wav_output_filename , now

    def deleteRecords(self,now, path, DAY, HOUR):
        if now.day == DAY and now.hour == HOUR:
            for file in os.listdir(path):  
                if (file.endswith('.wav')):
                    try:
                        os.remove(path+file)
                        cursor.execute("DELETE FROM records")
                        con.commit()
                    except Exception as e:
                        print(e)
                else:
                    pass
            for folder in os.listdir(logpath): 
                try: 
                    shutil.rmtree(logpath+folder)
                except Exception as e:
                    print(e)


    def deleteOneRecord(self, path):
        folderSize = 0     
        for file in os.listdir(path):  
            if (file.endswith('.wav')):
                    try:
                        fp = os.path.join(path, file)
                        folderSize += os.path.getsize(fp)
                    except Exception as e:
                        print(e)

        print("Folder size: " + str(folderSize) +"bytes" + " " + str((folderSize*0.000931)/1000000) + "Gb" )
        folderSizeGb = (folderSize*0.000931)/1000000
        if folderSizeGb >= 10:
            oldestrecord = oldest(path)
            oldestname = os.path.basename(oldestrecord).rsplit(".", 1)
            print(oldestrecord + " "+ "removed" + " "+ oldestname)
            os.remove(oldestrecord)
            cursor.execute("DELETE FROM records WHERE name=?", (oldestname,))
            con.commit()
        else:
            pass

    
    def recordAudio(self,samp_rate,chunk,record_secs):
        s = self.s
        print("recording")
        frames = []
        first_run = True
        # loop through stream and append audio chunks to frame array
        while(dbProcess.recording_process()):
            try:
                if first_run :
                    data =s.recv(4096)
                    first_run = False
                else:
                    data =s.recv(4096)
                    data_array = np.frombuffer(data, dtype='int16')
                    channel1 = data_array[1::2]
                    data = channel1.tostring()
            except Exception as e:
                data = bytes(0)
                first_run = True
                print(e)   
            frames.append(data)
        print("finished recording")
        return frames

#######################################################################################################################################################################

#initialization
form_1 = pyaudio.paInt16 # 16-bit resolution
chans = 2 # 1 channel
samp_rate = 44100 # 44.1kHz sampling rate
chunk = 4096 # 2^12 samples for buffer
SecondsPerChannel = 8 
DAY = 9
HOUR = 14


#adjusting time
path='/home/pi/fm-scanner/fm-scanner/static/'
logpath='/home/pi/fm-scanner/fm-scanner/logs/'

#classes
dbProcess = databaseBusiness(con,cursor)
recordingProcess = audioRecording(s)

NumberOfChannels = dbProcess.getNumberOfFrequencies()
record_secs = SecondsPerChannel * NumberOfChannels   # seconds to record

wav_output_filename, now = recordingProcess.getTime()
recordingProcess.deleteRecords(now,path, DAY, HOUR)

frames = recordingProcess.recordAudio(samp_rate,chunk,record_secs)


# save the audio frames as .wav file
wavefile = wave.open( path + wav_output_filename  + '.wav' ,'wb')
wavefile.setnchannels(chans)
wavefile.setsampwidth(audio.get_sample_size(form_1))
wavefile.setframerate(samp_rate*0.5)
wavefile.writeframes(b''.join(frames))
wavefile.close()

dbProcess.writeRecords()

con.close()

