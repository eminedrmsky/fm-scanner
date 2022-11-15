#Schedules working of module 0 to once in a hour

from abe import main
from time import sleep
import schedule

Frequency_Scan = main.SerialCommunication()

sleep(10)

Frequency_Scan.Module_0()
schedule.every(60).minutes.do(Frequency_Scan.Module_0)

while True:
  
    schedule.run_pending()
    sleep(1)