import pyaudio
import socket
from _thread import start_new_thread

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







