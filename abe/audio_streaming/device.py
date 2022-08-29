#use for getiing info about sound devices plugged in raspi. further information can be achieved by entering "alsamixer"
#to command window of raspi

import pyaudio
import pytz

pa = pyaudio.PyAudio()

for x in range(0, pa.get_device_count()):
    print(pa.get_device_info_by_index(x)) 
    print(pa.get_device_name(x))
print(pa.get_default_input_device_info())



