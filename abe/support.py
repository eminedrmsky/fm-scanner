import platform
import binascii
import numpy

import RPi.GPIO as GPIO
import fcntl
import time

import os
import argparse
import sqlite3

message_types = {
    "SET":b'1',
    "GET":b'2',
    "ERR":b'3',
    "ACK":b'4',
    "SYS":b'5',
}
command_types = {
    "RTD":b'R',
    "PSD":b'r',
    "FRQ":b'F',
    "POW":b'P',
    "SNR":b'S',
    "STA":b's',
    "POW":b'P',
    "VER":b'V',
    "CNF":b'C',
    "COU":b'c',
    "VOL":b'v',
    "PTY":b'p',
    "ANO":b'a',
}

message_types_reverse = {
    "1":'SET',
    "2":'GET',
    "3":'ERR',
    "4":'ACK',
    "5":'SYS',
}
command_types_reverse = {#TODO: create automatically
    'R':"RTD",
    'r':"PSD",
    'F':"FRQ",
    'P':"POW",
    'S':"SNR",
    's':"STA",
    'V':"VER",
    'C':"CNF",
    'c':"COU",
    'v':"VOL",
    'p':"PTY",
    'a':"ANO",
}
message_id = 0
header = b'ABE'

#Frekans listesinin hepsini alan kısım
con = sqlite3.connect("/home/pi/fm-scanner/fm-scanner/abe/get_status.db") 
cursor = con.cursor()

cursor.execute("SELECT freq FROM status")
data = cursor.fetchall() 
freqList=[i[0] for i in data]
con.close()
#TODO: database class'ının içine fonksiyon halinde yaz

def messageInit(addr, message_type, command_type, len):  # 1,1,c,2 => "ABE" + ID + ADDR + "1c" + \2
    global message_id
    message_id += 1
    message_id = message_id & 255
    return header + bytes([message_id]) + bytes([addr]) + message_types[message_type] + command_types[
        command_type] + bytes([len])  # message initialize
    # Header - id - addr - type - command - len - message - crc

def freqToHex (freq): # parse freq data (8840 in str format) to 2 bytes hex array 0x22 0x88
  return intToBytes(freq,2)

def intToBytes (num,count): # (256,2) => 0x01 0x0 (10,2) => 0x00 0x0A
    return num.to_bytes(count, byteorder='big')

def debugPrint (str,message,**options):
    if options.get("dir") == "SENT":
        print("---->>>\t", end = "")
    elif options.get("dir") == "RECV":
        print("<<<----\t", end = "")
    if str == "HEX":
        if(platform.system() == "Windows"):
            print (binascii.hexlify(message,' '))
        else:
            print (binascii.hexlify(message))
    elif str == "CHAR":
        print (message)
    elif str == "FORMAT":
        header = message[0:3]
        id = int(message[3])
        addr = message[4]
        typ = message_types_reverse[chr(message[5])]
        command = command_types_reverse[chr(message[6])]
        length = message[7]
        if(platform.system() == "Windows"):
            mesaj = binascii.hexlify(message[8:8+length],' ')
        else:
                    mesaj = binascii.hexlify(message[8:8+length])

        crc = message[8+length]
        print ("HEADER = {}\tID = {}\tADDR = {}\tTYPE = {}\tCOMMAND = {}\tLENGTH = {}\tCRC = {}\n\tMESSAGE = {}".format(header,id,addr,typ,command,length,crc,mesaj))
    else:
        print()


def messageFooter (str): # adds crc and footer \r\n to message
    crc = 0
    for i in str:#simple crc calculation. sum all of them :)
        crc = crc + i
    crc = crc & 255
    return bytes([crc]) + b'\r\n'

########################################################################################################################################

#sensor support
class I2C:
    """Wrapper class for I2C with raspberry Pi

    Open the "internal" I2C Port with driver or emulate an I2C Bus on GPIO
    """
    addr = 0
    dev = None
    gpio_scl = 0
    gpio_sda = 0
    delay = 0.001

    def open(self,addr=0, dev=1, scl=0, sda=0):
        """Open I2C-Port

        addr: I2C-Device Address
        dev:  I2C-Port (Raspberry Pi) B,B+,Pi 2 = 1 the first Pi = 0
              For I2C Emulation with GPIO, dev must be None
        scl:  GPIO-Pin for SCL
        sda:  GPIO-Pin for SDA
        """
        self.addr = addr
        self.dev = dev
        self.gpio_scl = scl
        self.gpio_sda = sda

        if (self.dev == None):
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.gpio_scl, GPIO.IN)  # SCL=1
            GPIO.setup(self.gpio_sda, GPIO.IN)  # SDA=1
        else:
            self.dev_i2c = open(("/dev/i2c-%s" % self.dev), 'rb+', 0)
            fcntl.ioctl(self.dev_i2c, 0x0706, self.addr)  # I2C Address

    def close(self):
        if (self.dev == None):
            GPIO.setup(self.gpio_scl, GPIO.IN)  # SCL=1
            GPIO.setup(self.gpio_sda, GPIO.IN)  # SDA=1
        else:
            self.dev_i2c.close()

    def write(self, data):
        """Write data to device

        :param data: one ore more bytes (int list)
        """
        if (self.dev == None):
            self._i2c_gpio_start()
            ack = self._i2c_gpio_write_byte(self.addr << 1)
            ack = self._i2c_gpio_write_byte(data[0])  # Trigger T measurement (no hold master)
            self._i2c_gpio_stop()
        else:
            d = bytes(data)
            self.dev_i2c.write(d)

    def read(self, size):
        """Read Bytes from I2C Device

        :param size: Number of Bytes to read
        :return: List with bytes
        """
        data = dict()
        if (self.dev == None):
            self._i2c_gpio_start()
            ack = self._i2c_gpio_write_byte((self.addr << 1) + 1)  # set READ-BIT
            # if not ack: print("I2C-ERROR: READ,NACK1")
            for i in range(size):
                ack = True if ((i + 1) < size) else False
                data[i] = self._i2c_gpio_read_byte(ack)
            self._i2c_gpio_stop()
        else:
            data = self.dev_i2c.read(size)
        return (data)

    ##########################################################################
    ##########################################################################
    #   GPIO Access
    ##########################################################################
    ##########################################################################

    def _i2c_gpio_start(self):
        """Send Start"""
        GPIO.setup(self.gpio_scl, GPIO.IN)  # SCL=1
        GPIO.setup(self.gpio_sda, GPIO.IN)  # SDA=1
        time.sleep(2 * self.delay)
        GPIO.setup(self.gpio_sda, GPIO.OUT)  # SDA=0
        GPIO.output(self.gpio_sda, 0)
        time.sleep(2 * self.delay)
        GPIO.setup(self.gpio_scl, GPIO.OUT)  # SCL=0
        GPIO.output(self.gpio_scl, 0)

    def _i2c_gpio_stop(self):
        """Send Stop"""
        GPIO.setup(self.gpio_sda, GPIO.OUT)  # SDA=0
        GPIO.output(self.gpio_sda, 0)
        time.sleep(2 * self.delay)
        GPIO.setup(self.gpio_scl, GPIO.IN)  # SCL=1
        time.sleep(2 * self.delay)
        GPIO.setup(self.gpio_sda, GPIO.IN)  # SDA=1
        time.sleep(2 * self.delay)

    def _i2c_gpio_write_byte(self, data):
        """Write a single byte"""
        for i in range(8):  # stop
            if (data & 0x80):
                GPIO.setup(self.gpio_sda, GPIO.IN)  # SDA=1
            else:
                GPIO.setup(self.gpio_sda, GPIO.OUT)  # SDA=0
                GPIO.output(self.gpio_sda, 0)
            data = data << 1
            time.sleep(self.delay)
            GPIO.setup(self.gpio_scl, GPIO.IN)  # SCL=1
            time.sleep(self.delay)
            # Clockstretching ToDo
            GPIO.setup(self.gpio_scl, GPIO.OUT)  # SCL=0
            GPIO.output(self.gpio_scl, 0)
            time.sleep(self.delay)

        GPIO.setup(self.gpio_sda, GPIO.IN)  # SDA=1
        time.sleep(self.delay)
        GPIO.setup(self.gpio_scl, GPIO.IN)  # SCL=1
        time.sleep(self.delay)
        # Clockstretching ToDo
        ack = True if (GPIO.input(self.gpio_sda) == 0) else False
        GPIO.setup(self.gpio_scl, GPIO.OUT)  # SCL=0
        GPIO.output(self.gpio_scl, 0)
        time.sleep(self.delay)
        return (ack)  # SCL=0 SDA=1

    def _i2c_gpio_read_byte(self, ack):
        """Read a single byte"""
        data = 0
        for i in range(8):  # stop
            time.sleep(self.delay)
            GPIO.setup(self.gpio_scl, GPIO.IN)  # SCL=1
            time.sleep(self.delay)
            # Clockstretching ToDo
            data = data << 1
            if (GPIO.input(self.gpio_sda)):
                data |= 1
            else:
                data &= ~1
            GPIO.setup(self.gpio_scl, GPIO.OUT)  # SCL=0
            GPIO.output(self.gpio_scl, 0)

        # ACK Bit ausgeben
        if (ack):
            GPIO.setup(self.gpio_sda, GPIO.OUT)  # SDA=0
            GPIO.output(self.gpio_sda, 0)
        else:
            GPIO.setup(self.gpio_sda, GPIO.IN)  # SDA=1

        time.sleep(self.delay)
        GPIO.setup(self.gpio_scl, GPIO.IN)  # SCL=1
        time.sleep(self.delay)
        # Clockstretching ToDo
        GPIO.setup(self.gpio_scl, GPIO.OUT)  # SCL=0
        GPIO.output(self.gpio_scl, 0)
        time.sleep(self.delay)
        GPIO.setup(self.gpio_sda, GPIO.IN)  # SDA=1  freigeben
        return (data)

####################################################################################################################################


#####################################################################################################################################

#db support
class DatabaseProcess():
   #DB 
    def __init__(self, con, cursor):
        self.con = con
        self.cursor = cursor
   
    def create_table(self):
        conn = self.con
        crsr = self.cursor
        crsr.execute("CREATE TABLE IF NOT EXISTS status (freq INT PRIMARY KEY, resp1 INT, rssi INT, snr INT)") 
        conn.commit()

    def add_value(self,date,freq,resp1,rssi,snr, info, temp, hum):
        conn = self.con
        crsr = self.cursor
        crsr.execute("INSERT INTO data VALUES(?,?,?,?,?,?,?,?)",(date,freq,resp1,rssi,snr,info,temp,hum))
        conn.commit()

    def get_all_data(self): #TÜM SESLERİ 30 SN ARALIKLA DİNLEMEK İÇİN
        crsr = self.cursor
        crsr.execute("Select * From status") # Bütün bilgileri alıyoruz.
        data = crsr.fetchall() # Veritabanından bilgileri çekmek için fetchall() kullanıyoruz.

        print("Status Tablosunun bilgileri.....")
        for i in data:
            print(i[2])

    def get_data(self, frequency): #SEÇİLEN FREKANSTAKİ SESİ DİNLEMEK İÇİN
        crsr = self.cursor
        crsr.execute("Select * From status where freq = ?",(frequency,)) # Sadece freq değeri arayüz üzerinden seçilmiş olan frekansı alıyoruz.
        data = crsr.fetchall()

    def update_data(self, frequency, resp1, rssi, snr, stat):
        conn = self.con
        crsr = self.cursor
        crsr.execute("Update status set resp1 = ?, rssi = ?, snr = ?, stat=? where freq = ?",(resp1, rssi, snr, stat, frequency))
        conn.commit()

    def update_stat(self, freq):
        conn = self.con
        crsr = self.cursor
        crsr.execute("UPDATE status SET stat = ? where freq = ?",(0, freq))
        conn.commit()

    def update_stat_all(self):
        conn = self.con
        crsr = self.cursor
        crsr.execute("UPDATE status SET stat = 0 ")
        conn.commit()

    def get_FrequencyList(self): #SEÇİLEN FREKANSTAKİ SESİ DİNLEMEK İÇİN
        crsr = self.cursor
        crsr.execute("Select freq From status where stat = 1") # Sadece freq değeri arayüz üzerinden seçilmiş olan frekansı alıyoruz.
        data = crsr.fetchall() 
        frequencylist= [] 
        for frequency in data:
            frequencylist.append(frequency[0])
        return numpy.array(frequencylist)

    def get_data_serial(self): #databaseden dinleme komutu almak için
        crsr = self.cursor
        crsr.execute("SELECT stat FROM dinleme WHERE var = 'listen'") 
        data = crsr.fetchall()
        return data[0][0]
    
    def serial_available(self):
        conn = self.con
        crsr = self.cursor
        crsr.execute("UPDATE dinleme SET stat = 0 where var = 'listen'")
        conn.commit()
    
    def serial_bussy(self):
        conn = self.con
        crsr = self.cursor
        crsr.execute("UPDATE dinleme SET stat = 1 where var = 'listen'")
        conn.commit()

    def update_temp(self, date, temp, hum):
        conn = self.con
        crsr = self.cursor
        crsr.execute("INSERT INTO medium VALUES(?,?,?)",(date, temp, hum))
        conn.commit()

    def end_recording(self):
        conn = self.con
        crsr = self.cursor
        crsr.execute("UPDATE dinleme SET stat = 0 where var = 'record'")
        conn.commit()
    
    def start_recording(self):
        conn = self.con
        crsr = self.cursor
        crsr.execute("UPDATE dinleme SET stat = 1 where var = 'record'")
        conn.commit()
    











