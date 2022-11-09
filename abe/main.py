#!/usr/bin/env python3
import serial
from abe import business
from time import sleep
from abe import support
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import *
import sqlite3 

logger = logging.getLogger(__name__)


#if __name__ == '__main__':
try:
    #SERIAL
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    ser.flush()
    serial_available = True
    print("Bağlantı Sağlandı")

    #SENSÖR.
    sht21 = business.SHT21()

    #PİL
    #TODO: Eklenen Class'a bak.

    #DB
    con = sqlite3.connect("/home/pi/fm-scanner/fm-scanner/abe/get_status.db") 
    cursor = con.cursor()
    cursor.execute("UPDATE dinleme SET stat = 0 where var = 'listen'")
    con.commit()

    #LOGGING
    logsFolder = os.path.join("logs")
    now = datetime.now()
    logFileFolder = os.path.join(logsFolder,now.strftime("%d.%m.%Y"))
    os.makedirs(logFileFolder,exist_ok= True)
    logFilePath = os.path.join(logFileFolder, "ABE")
    logging.basicConfig(level=logging.DEBUG,
        handlers=[
            logging.handlers.TimedRotatingFileHandler(logFilePath, when = 'M')
        ])

except Exception as e:
    print(e)
    serial_available = False
    print("Bağlantı Yok")


class SerialCommunication(object): 

#scan frequencies given in database
    def Module_0(self):
        
        #Rpi
        con = sqlite3.connect("/home/pi/fm-scanner/fm-scanner/abe/get_status.db") 
        cursor = con.cursor()
        raspberryProccess = business.RaspberryPiProccess(ser, serial_available)

        #DB
        dbProccess = support.DatabaseProcess(con, cursor)
        dbProccess.create_table()
           
        print(support.freqList)
        #Modül 0 için işlemler => Sadece Okuma Modülü..

        os.system("python3 abe/audio_streaming/audio_record.py &") # for recordings
        freq_index_module0 = 0
        dbProccess.start_recording()
        while (freq_index_module0 < len(support.freqList) ):
            if dbProccess.get_data_serial() == 0:
                print("serial available")
                dbProccess.serial_bussy()
                raspberryProccess.set_frequency_module0 = freq_index_module0
                sleep(2)
                freq_index_module0 += 1
                resp1, freq, rssi, snr = raspberryProccess.get_status_module0  
                dbProccess.serial_available()
                now = datetime.now()
                print("Frequency: ", freq)
                print("RESP1: ", resp1)
                print("RSSI: ", rssi)
                print("SNR: ", snr)

                (temperature, humidity) = sht21.measure(1)  # I2C-1 Port
                print("Temperature: %s °C  Humidity: %s %%" % (temperature, humidity))
                sleep(1)
                dbProccess.update_temp(now, temperature, humidity)

                if temperature > 60.0 :
                   logger.warning(f"{now} - Temperature, higher than {temperature} degrees!!")

                if (snr == 0):
                    try:
                        dbProccess.update_data(freq,resp1,rssi,snr,"There is no sound!")
                        dbProccess.add_value(now,freq,resp1,rssi,snr, "There is no sound!",0,0)  #convert zeros to temperature and humidity
                    except Exception as e:
                        print(e)
                else:
                    try:
                        dbProccess.update_data(freq,resp1,rssi,snr,"Sound is OK!")
                        dbProccess.add_value(now,freq,resp1,rssi,snr,"Sound is OK!",0,0)   #convert zeros to temperature and humidity
                    except Exception as e:
                        print(e)

                logger.info(f"{now} - freq: {freq} - resp1: {resp1}, rssi: {rssi}, snr: {snr}")
                sleep(5)
                ser.flush()
            else:
                print("serial not available")
                sleep(1)
        
        dbProccess.end_recording()
            
        
            
            
# Listen all frequencies in database
    def Module_1(self):
        #Rpi
        con = sqlite3.connect("/home/pi/fm-scanner/fm-scanner/abe/get_status.db") 
        cursor = con.cursor()
        raspberryProccess = business.RaspberryPiProccess(ser, serial_available)

        #DB
        dbProccess = support.DatabaseProcess(con, cursor)
        dbProccess.create_table()
   
        print(support.freqList)
        freq_index_module1 = 0
        while (freq_index_module1 < len(support.freqList)):
            if dbProccess.get_data_serial() == 0:
                dbProccess.serial_bussy()
                raspberryProccess.set_frequency_module1 = freq_index_module1
                sleep(1)
                freq_index_module1 += 1
                resp1, freq, rssi, snr= raspberryProccess.get_status_module1
                dbProccess.serial_available()
                now = datetime.now()
                print("Frequency: ", freq)
                print("RESP1: ", resp1)
                print("RSSI: ", rssi)
                print("SNR: ", snr)
                    
                if(snr == 0):
                    #Arayüz üzerinden bu frekansta ses olmadığını belirt.
                    logger.warning(f"{now} - {freq} => Bu frekansta ses yok!")
                    pass
                    
                else:
                    #Arayüz üzerinden bu frekansta ses olduğunu belirt.
                    logger.info(f"{now} - {freq} => Frekansındaki ses dinleniyor..")
                    pass

                sleep(30)
                ser.flush()
            else:
                sleep(1)

#listen only one chosen frequency 
    def Module_1_One_Frequency(self, CurrentChannel):
                    #Rpi
        con = sqlite3.connect("/home/pi/fm-scanner/fm-scanner/abe/get_status.db") 
        cursor = con.cursor()
        raspberryProccess = business.RaspberryPiProccess(ser, serial_available)

        #DB
        dbProccess = support.DatabaseProcess(con, cursor)
        dbProccess.create_table()
        sleep(1)
        print("ikinci kısma girdi")
        if dbProccess.get_data_serial() == 0:
            dbProccess.serial_bussy()

            raspberryProccess.set_frequency_module1= CurrentChannel
            sleep(1)
            resp1, freq, rssi, snr = raspberryProccess.get_status_module1
            dbProccess.serial_available()
            now = datetime.now()
            print("Frequency: ", freq)
            print("RESP1: ", resp1)
            print("RSSI: ", rssi)
            print("SNR: ", snr)

            if(snr == 0):
                #Arayüz üzerinden bu frekansta ses olmadığını belirt.
                logger.warning(f"{now} - {freq} => Bu frekansta ses yok!")
                pass
                    
            else:
                #Arayüz üzerinden bu frekansta ses olduğunu belirt.
                logger.info(f"{now} - {freq} => Frekansındaki ses dinleniyor..")
                pass

            #TODO:Arayüzü oku. => db listen data 
            ser.flush()
        else:
            sleep(1)


    def Module_0_One_Frequency(self, CurrentChannel):
                    #Rpi
        con = sqlite3.connect("/home/pi/fm-scanner/fm-scanner/abe/get_status.db") 
        cursor = con.cursor()
        raspberryProccess = business.RaspberryPiProccess(ser, serial_available)

        #DB
        dbProccess = support.DatabaseProcess(con, cursor)
        dbProccess.create_table()
        sleep(1)
        print("ikinci kısma girdi")
        if dbProccess.get_data_serial() == 0:
            dbProccess.serial_bussy()
            raspberryProccess.set_frequency_module0= CurrentChannel
            sleep(1)
            resp1, freq, rssi, snr = raspberryProccess.get_status_module0
            dbProccess.serial_available()
            now = datetime.now()
            print("Frequency: ", freq)
            print("RESP1: ", resp1)
            print("RSSI: ", rssi)
            print("SNR: ", snr)

            if(snr == 0):
                #Arayüz üzerinden bu frekansta ses olmadığını belirt.
                logger.warning(f"{now} - {freq} => Bu frekansta ses yok!")
                pass
                    
            else:
                #Arayüz üzerinden bu frekansta ses olduğunu belirt.
                logger.info(f"{now} - {freq} => Frekansındaki ses dinleniyor..")
                pass
        else:
            sleep(1)
        
            


            

    
