#Schedules working of module 0 to once in a hour

from abe import main
from time import sleep
import schedule
import sqlite3

con = sqlite3.connect("/home/pi/fm-scanner/fm-scanner/abe/get_status.db") 
cursor = con.cursor()
Frequency_Scan = main.SerialCommunication()

def get_interval(con,cursor): #databaseden dinleme komutu almak için
    cursor.execute("SELECT stat FROM dinleme WHERE var = 'interval'") 
    data = cursor.fetchall()
    return data[0][0]

interval = get_interval(con,cursor)
print(interval)

Frequency_Scan.Module_0()
sleep(10)
schedule.every(interval).minutes.do(Frequency_Scan.Module_0)

while True:
  
    schedule.run_pending()
    sleep(1)