from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from datetime import datetime
import os

path = "/home/pi/fm-scanner/fm-scanner/"

class Anouncement:
    def __init__(self, row):
        self.date = row[0].value
        self.groupName = row[1].value
        self.startTime = row[2].value
        self.endTime = row[3].value
        self.anounceID = row[4].value
        self.radioTime = row[5].value

def readWorkBook(path):
    for file in os.listdir(path):
        if (file.endswith("xlsx")):
            try:
                wb = load_workbook(path+file)
                ws = wb.active
                print( "Accessed worksheet"+ " " +file)
            except Exception as e:
                print(e)

    return wb, ws

class manageExcel():
    def __init__(self, wb,ws):
        self.wb = wb
        self.ws = ws

    def appendHeader(self):
        wb = self.wb
        ws = self.ws
        ws.append(['Date', 'Group Name', 'Starting Time', 'Ending Time', 'Anouncement ID', 'After Radio Time'])
        wb.save('data.xlsx')

    def appendData(self, date, groupName, startTime, endTime, anounceID, radioTime):
        wb = self.wb
        ws = self.ws
        try:
            ws.append([date, groupName, startTime, endTime, anounceID, radioTime])
        except Exception as e:
            print(e)
        wb.save('data.xlsx')

    def readAllData(self):
        wb = self.wb
        ws = self.ws
        for columnData in ws['A']:
            print(columnData.value)

    def filterWithDate(self, startDate, endDate, startTime = None, endTime = None):
        wb = self.wb
        ws = self.ws
        
        if startTime == None and endTime == None:
            startDate = datetime.strptime(startDate, '%d.%m.%Y')
            endDate = datetime.strptime(endDate, '%d.%m.%Y')
            
        else:
            startDate = datetime.strptime(startDate + " "+ startTime, '%d.%m.%Y %H:%M')
            endDate = datetime.strptime(endDate + " "+ endTime, '%d.%m.%Y %H:%M')

        rowCounter = 0
        anounces = []
        filteredAnouncement = []
        for columnData in ws['A']:
            rowCounter = rowCounter + 1
            anounces.append(Anouncement(ws[rowCounter]))
            try:
                anounceStart = datetime.strptime(anounces[rowCounter-1].date + " " +anounces[rowCounter-1].startTime, '%d.%m.%Y %H:%M')
                if anounceStart >= startDate and anounceStart <= endDate:
                    filteredAnouncement.append(Anouncement(ws[rowCounter]))
                else:
                    continue
            except Exception as e:
                print(e)
                continue
        return filteredAnouncement

#################################################################################################################################################################################


# wb = Workbook()
wb, ws = readWorkBook(path)
# ws.title = "Data"

manEx = manageExcel(wb,ws)

filteredAnouncement = manEx.filterWithDate("24.10.2022","25.10.2022", "10:40", "12:00")

for anounce in filteredAnouncement:
    print(anounce.date)
    print(anounce.startTime)



        


