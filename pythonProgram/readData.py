'''
import serial
import csv
import sys
import time
import matplotlib.pyplot as plt

if __name__ == '__main__':

    csvfile = "data.csv"
    # kết nối arduino với raspberry, '/dev/ttyUSB0' là tên cổng USB của raspberry, 
    # tên này có thể thay đổi nếu thay đổi cổng trên raspberry
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    ser.reset_input_buffer()
    time.sleep(0.1)

    dataList = []
    count = 0

    # cấu hình để vẽ đồ thị
    plt.ion()
    fib, ax = plt.subplots()
    ax.set_xlabel('Time')
    ax.set_ylabel('Voltage')
    xdata, ydata = [], []
    line, = ax.plot(xdata, ydata)

    while True:
        if ser.in_waiting > 0:
            # đọc chuỗi dữ liệu nhận được từ arduino lưu vào biến data
            data = ser.readline().decode('uft-8').rstrip()

            # tách chuỗi nhận được bởi dấu phẩy lưu vào biến temp
            temp = data.split(',')

            # chuyển dữ liệu từ kiểu chuỗi sang kiểu số thực
            temp = [float(val) for val in temp]

            # lưu dữ liệu vào mảng dataList
            dataList.append(temp)

            # biến count là biến đếm số lần để tính trung bình
            count += 1

            # tính trung bình 10 dữ liệu
            if count == 10:

                # tính trung bình 10 dữ liễu lưu vào mảng avgData
                avgData = [round(sum(col)/10, 2) for col in zip(*dataList)]
                print(avgData)

                # tạo biến thời gian 
                timeC = time.strftime("%I") + ':' + time.strftime("%M") + ':' + time.strftime("%S")

                # lưu vào LibreOffice Calc
                strData = [timeC] + avgData

                # mở file data/data.csv và lưu dữ liệu
                with open("data" + csvfile, 'a') as output:
                    writer = csv.writer(output, delimiter = ',', lineterminator = '\n')
                    writer.writerow(strData)

                # vẽ đồ thị voltage theo thời gian
                voltage = float(avgData[0])
                xdata.append(time.time())
                ydata.append(voltage)
                line.set_xdata(xdata)
                line.set_ydata(ydata)
                ax.relim()
                ax.autoscale_view()
                fig.canvas.draw()
                plt.pause(0.001)

                # reset giá trị sau khi tính giá trị trung bình
                count = 0
                dataList = []
'''


import os
from google.auth.transport.requests import Request
from google.oauth2.credentials  import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from datetime import datetime
import time 

import serial
import csv

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SPREADSHEET_ID = "1qEUcCAYP2UQXzkSIRtocACFyQfVTbTB0N3ZLQ_k1IoM"

def main():

    csvfile = "data.csv"
    # kết nối arduino với raspberry, '/dev/ttyUSB0' là tên cổng USB của raspberry, 
    # tên này có thể thay đổi nếu thay đổi cổng trên raspberry
    # ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    ser = serial.Serial('COM5', 9600, timeout=1)
    ser.reset_input_buffer()
    time.sleep(0.1)

    dataList = []
    count = 0

    credentials = None
    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            credentials = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(credentials.to_json())

    while True:
        if ser.in_waiting > 0:
            # đọc chuỗi dữ liệu nhận được từ arduino lưu vào biến data
            data = ser.readline().decode('utf-8').rstrip()
            print(data)
            print('\n')

            # tách chuỗi nhận được bởi dấu phẩy lưu vào biến temp
            temp = data.split(',')

            # chuyển dữ liệu từ kiểu chuỗi sang kiểu số thực
            temp = [float(val) for val in temp]

            # lưu dữ liệu vào mảng dataList
            dataList.append(temp)

            # biến count là biến đếm số lần để tính trung bình
            count += 1
            print(count)

            # tính trung bình 10 dữ liệu
            if count == 10:

                # tính trung bình 10 dữ liễu lưu vào mảng avgData
                avgData = [round(sum(col)/10, 2) for col in zip(*dataList)]
                print(avgData)
                print('\n')

                # tạo biến thời gian 
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # lưu vào LibreOffice Calc
                strData = [[timestamp] + avgData]

                # mở file data/data.csv và lưu dữ liệu
                # with open("data" + csvfile, 'a') as output:
                #     writer = csv.writer(output, delimiter = ',', lineterminator = '\n')
                #     writer.writerow(strData)

                try:
                    service = build("sheets", "v4", credentials=credentials)
                    sheets = service.spreadsheets()


                    range_to_update = "RawData!A:S"  # Range from column A to S
                    sheets.values().append(spreadsheetId=SPREADSHEET_ID, range=range_to_update,
                                        valueInputOption="USER_ENTERED", body={"values": strData}).execute()
                    
                    range_to_insert = "RawData!A2:S2"  # Range for row 2
                    sheets.values().update(spreadsheetId=SPREADSHEET_ID, range=range_to_insert,
                                    valueInputOption="USER_ENTERED", body={"values": strData}).execute()
                except  HttpError as error:
                    print(error)
                    
                # reset giá trị sau khi tính giá trị trung bình
                count = 0
                dataList = []

        # for row in range(3, 20):
            
        #     float_array = [220, 5, 0.88, 0.9, 220, 5, 0.88, 0.9, 220, 5, 0.88, 0.9]

        #     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #     values = [[timestamp] + float_array]  # Create a 2D array with timestamp and float_array
        #     range_to_update = "RawData!A:S"  # Range from column A to S
        #     sheets.values().append(spreadsheetId=SPREADSHEET_ID, range=range_to_update,
        #                         valueInputOption="USER_ENTERED", body={"values": values}).execute()
            
        #     range_to_insert = "RawData!A2:S2"  # Range for row 2
        #     sheets.values().update(spreadsheetId=SPREADSHEET_ID, range=range_to_insert,
        #                        valueInputOption="USER_ENTERED", body={"values": values}).execute()
        #     time.sleep(2)

if __name__ == "__main__":
    main()