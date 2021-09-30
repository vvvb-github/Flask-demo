#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import csv
import sqlite3
from Utils import is_number

class FileHelper():

    def __init__(self, fileRoot=""):
        self.fileRootPath = fileRoot

    def ReadCSV(self, filepath, exceptVal=9999.9):
        filepath = self.fileRootPath + filepath
        # 数据时间
        times = []
        # 温度1（2、3）、海面温度（红外海温）、湿度1（2、3）、真实风速1（2、3）、大气压力
        dataset = []
        rowNum = 0
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if rowNum == 0:
                    rowNum += 1
                    continue
                datas = [exceptVal, exceptVal, exceptVal, exceptVal, exceptVal]
                times.append(row[0])
                for i in range(len(row)):
                    if i == 5 or i == 12 or i == 19:
                        # 处理异常值
                        if datas[0] == exceptVal:
                            datas[0] = float(row[i])
                    if i == 1 or i == 2:
                        if datas[1] == exceptVal:
                            datas[1] = float(row[i])
                    if i == 6 or i == 13 or i == 20:
                        if datas[2] == exceptVal:
                            datas[2] = float(row[i])
                    if i == 10 or i == 17 or i == 24:
                        if datas[3] == exceptVal:
                            datas[3] = float(row[i])
                    if i == 3:
                        if datas[4] == exceptVal:
                            datas[4] = float(row[i])
                dataset.append(datas)
        return times, dataset

    # 说明：字符位置11-16为气压，19-23为高度，26-31为气温，34-38为湿度，48-50为风向，53-57为风速，
    # 组合为[高度、气温、压强、风速、湿度、风向]
    def ReadTxt(self, filepath="gaokong.txt", limit=3000):
        filepath = self.fileRootPath + filepath
        flag = True
        dataset = []
        with open(filepath, "r") as f:
            for line in f.readlines():
                line = line.strip('\n')
                if flag:
                    flag = False
                    continue
                altitude = float(line[18:23])
                if altitude > limit:
                    break
                press = float(line[10:16])
                temperature = float(line[25:31])
                humidity = float(line[33:38])
                wind = float(line[52:57])
                direction = float(line[47:50])
                dataset.append([altitude, temperature, press, wind, humidity, direction])
        return dataset

    # 读取TPU格式的文件
    # 读取snd_2144102019.tpu文件格式的代码 为[序号，温度，湿度，气压，GPS测高，气压反算高度]
    # 得到的最后结果，取前10000m的[alt(高度), tem(温度), pre(压强), hum(湿度)]
    def ReadTPU(self, filepath="F:\\SomeCacheFile\\Atmos_Data\\data\\snd_2144102019.tpu", limit=10000):
        filepath = self.fileRootPath + filepath
        flag = True
        dataset = []
        with open(filepath, "r") as f:
            for line in f.readlines():
                line = line.strip('\n').split()
                if flag:
                    flag = False
                    continue
                alt = float(line[5])
                if alt > limit:
                    break
                tem = float(line[1])
                hum = float(line[2])
                pre = float(line[3])
                dataset.append([alt, tem, pre, hum])
        return dataset

    # 读取湿度HPC文件
    def ReadHPC(self, filepath):
        filepath = self.fileRootPath + filepath
        height = []
        humidity_re = []
        l = 0
        with open(filepath, "r", encoding='utf-8') as f:
            for line in f.readlines():
                line = line.strip('\n')
                if (l == 3):
                    temp = line.split('#')
                    temp = temp[0].split()
                    humidity_max = float(temp[0])
                if (l == 7):
                    temp = line.split(',')
                    for i in range(len(temp) - 1):
                        height.append(float(temp[i]))
                    h = temp[len(temp) - 1].split('#')
                    height.append(float(h[0]))
                if (l > 8):
                    humidity = []
                    temp = line.split(',')
                    year = float(temp[0])
                    month = float(temp[1])
                    day = float(temp[2])
                    hour = float(temp[3])
                    min = float(temp[4])
                    second = float(temp[5])
                    RainFlag = int(temp[6])
                    for i in range(7, len(temp)):
                        # 相对湿度计算
                        humidity.append(float(temp[i]) / humidity_max)
                    humidity_re.append(humidity)
                l = l + 1

    # 读取温度廓线文件TPC
    def ReadTPC(self, filepath):
        filepath = self.fileRootPath + filepath
        height = []
        temperature_re = []
        l = 0
        with open(filepath, "r", encoding='utf-8') as f:
            for line in f.readlines():
                line = line.strip('\n')
                if (l == 7):
                    temp = line.split(',')
                    for i in range(len(temp) - 1):
                        height.append(float(temp[i]))
                    h = temp[len(temp) - 1].split('#')
                    height.append(float(h[0]))
                if (l > 8):
                    temperature = []
                    temp = line.split(',')
                    year = float(temp[0])
                    month = float(temp[1])
                    day = float(temp[2])
                    hour = float(temp[3])
                    min = float(temp[4])
                    second = float(temp[5])
                    RainFlag = int(temp[6])
                    for i in range(7, len(temp)):
                        temperature.append(float(temp[i]))
                    temperature_re.append(temperature)
                l = l + 1

    # 读取DDB3文件，获取其中的时间和气温、海温、相对湿度、风速、压强
    def ReadDDB3(self, filepath):
        conn = sqlite3.connect(filepath)
        c = conn.cursor()
        c.execute("SELECT Time,Temperature1,Humidity1,TemperatureSeaIR,Pressure,WinspeedR1 from 实时数据")
        result = c.fetchall()
        times = []
        dataset = []
        for i in range(len(result)):
            if (result[i][0] != None and result[i][1] != None and result[i][2] != None and result[i][3] != None and
                    result[i][4] != None and result[i][5] != None):
                times.append(result[i][0])
                dataset.append([result[i][1], result[i][3], result[i][2], result[i][5], result[i][4]])
        return times, dataset

    # 返回的是[高度，温度，压强，湿度，风速，风向]
    def ReadGaokong1(self, filepath, limit=3000):
        dataset = []
        l = 0
        with open(filepath, "r", encoding='ANSI') as f:
            for line in f.readlines():
                line = line.strip('\n')
                if (l >= 2):
                    temp = line.split()
                    temperature = float(temp[2])
                    press = float(temp[3])
                    humidity = float(temp[4])
                    altitude = float(temp[7])
                    direction = float(temp[5])
                    wind = float(temp[6])
                    if altitude > limit:
                        break
                    dataset.append([altitude, temperature, press, humidity, wind, direction])
                l = l + 1
        return dataset

    # 返回的是[高度，温度，压强，湿度，风速，风向]
    def ReadGaokong2(self, filepath, limit=3000):
        dataset = []
        l = 0
        with open(filepath, "r", encoding='utf-8') as f:
            for line in f.readlines():
                line = line.strip('\n')
                if (l >= 14):
                    temp = line.split()
                    temperature = float(temp[1])
                    press = float(temp[2])
                    humidity = float(temp[3])
                    altitude = float(temp[4])
                    direction = float(temp[7])
                    wind = float(temp[8])
                    if altitude > limit:
                        break
                    dataset.append([altitude, temperature, press, humidity, wind, direction])
                l = l + 1
        return dataset

    # 返回的是[高度，温度，压强，湿度]
    def ReadGaokong3(self, filepath, limit=3000):
        dataset = []
        l = 0
        with open(filepath, "r", encoding='utf-8') as f:
            for line in f.readlines():
                line = line.strip('\n')

                if (l >= 3):
                    temp = line.split()
                    if (is_number(temp[1]) and is_number(temp[2]) and is_number(temp[3]) and is_number(temp[5])):
                        temperature = float(temp[1])
                        press = float(temp[3])
                        humidity = float(temp[2])
                        altitude = float(temp[5])
                        # print(temperature)
                        # print(press)
                        # print(humidity)
                        # print(altitude)
                        if altitude > limit:
                            break
                        dataset.append([altitude, temperature, press, humidity])
                l = l + 1
        return dataset