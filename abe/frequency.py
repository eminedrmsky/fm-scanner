from abe.support import *
import logging
from time import sleep
from datetime import *


logger = logging.getLogger(__name__)

class BaseFrequencyProccess(object):
    def __set__(self, obj, value):
        ser = obj.ser
        serial_available = obj.serial_available

        print("setfreq")
        message = bytes()
        message += messageInit((1 * 10), "SET", "FRQ", 3)  # will send every freq twice

        message += bytes([self.module_id])
        message += freqToHex(int(self.freqList[value]))

        message += messageFooter(message)

        if (serial_available == True):
            ser.write(message)
            debugPrint('HEX', message, dir="SENT")
            ack = ser.read_until(b'\r\n')
            debugPrint("HEX", ack, dir="RECV")
            err = ser.read_until(b'\r\n')
            debugPrint("HEX", err, dir="RECV")


    def __get__(self, obj, owner):
        ser = obj.ser
        serial_available = obj.serial_available

        print("get status")

        message = bytes()
        message += messageInit((1 * 10), "GET", "STA", 6)

        message += bytes([self.moduleId])
        message += bytes([0])  # resp1
        message += bytes([0])  # freq[0]
        message += bytes([0])  # freq[1]
        message += bytes([0])  # RSII
        message += bytes([0])  # SNR

        message += messageFooter(message)

        if (serial_available == True):
            ser.write(message)
            debugPrint("HEX", message, dir="SENT")

            
            ack = ser.read_until(b'\r\n')
            debugPrint("HEX", ack, dir="RECV")
            
        if(len(ack) == 12):
            if (ack[8] == 0 or ack[8] == 1):  # module_id 1 ya da 0 ise (çünkü 2 modülümüz var)
                answer = ser.read_until(b'\r\n')
                # gelen mesaj şöyle bir şey (.... 06 00 ab cd ef gh jk ...)
                #  06: message length   |   00: module_id
                # kalan 5 byte bizim return değerlerimiz olacak, iki tanesi frekans için mesela)
                debugPrint("HEX", answer, dir="RECV")
                if(int(len(answer)) >= 12):
                    try:
                        resp1 = answer[9]
                        freq = answer[10] * 256 + answer[11]
                        rssi = answer[12]
                        snr = answer[13]
                    except Exception as e:
                        print(e)
                        return 1,1,1,1
                    
                    return resp1, freq, rssi, snr, 
                else:
                    now = datetime.now()
                    logger.warning(f"{now} - There is no answer from the modules!")
                    return 0,0,0,int(len(answer))

        else:
            now = datetime.now()
            logger.warning(f"{now} - There is no ACK coming from the modules")           
            return 1, 1, 1, len(ack)

    