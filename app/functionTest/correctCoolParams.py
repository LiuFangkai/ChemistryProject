import csv
from operator import itemgetter

import  numpy as np
import math
#图标用中文显示
from scipy import optimize

v = 10
#步骤1，读读降温数据（确保数据是从大到小）
def readCsv(filename):
    with open(filename) as f:
        table = []
        for line in f:
            col = line.split(',')
            col[0] = float(col[0])
            col[1] = float(col[1])
            table.append(col)
        table_sorted = sorted(table, key=itemgetter(0),reverse=False) #对降温数据进行排序，默认为升序排列
        x0 = []
        y0 = []
        for row in table_sorted:
            x0.append(row[0])
            y0.append(row[1])
    return x0,y0

def f(x,a,b):
    return a*x+b

# 步骤2，进行基线修正，确定a，b两点，返回修正后的坐标，存在x，y中
#降温数据从温度高的地方先修正
def correct(filename,**kwargs):
    x0, y0 = readCsv(filename)
    maxy = y0.index(max(y0))  # 最低温度点
    x = []
    y = []
    for i in range(len(y0)):
        y.append(y0[i] / y0[maxy] * 100)
        x.append(x0[i])

    # 用来寻找终点b
    count = 0
    for i in range(len(x)):
        count = count + 1  # count为5℃所包含的数据点
        if x[i] - x[0] >= 5:
            break

    # 剔除升温数据温度最后5℃包含的数据点
    for i in range(maxy, len(x) - count, 1):
        xx = [x[i], x[i + count]]
        yy = [y[i], y[i + count]]
        a, b = optimize.curve_fit(f, xx, yy)[0]
        angle = math.atan(a) * 180 / math.pi  # 将斜率转换为角度
        # print("%f-%f:%f" % (x[i], x[i+count], angle))
        if angle < 5 and angle > 0:  # 如果角度小于5，取该点为终点
            temp1 = i
            break

    # 用来寻找起点a
    # 去掉降温数据温度开始5℃的数据点
    for i in range(maxy, count + 1, -1):
        xx = [x[i - count], x[i]]
        yy = [y[i - count], y[i]]
        a, b = optimize.curve_fit(f, xx, yy)[0]
        angle = math.atan(a) * 180 / math.pi
        # print("%f-%f:%f" % (x[i - count], x[i], angle))
        if angle < 4:  # 如果角度小于5，取该点为终点
            temp = i
            break

    # # 在ab之间的点，存入x,y中
    # print('correct')
    # print(x0[temp], y0[temp])
    # print(x0[temp1], y0[temp1])
    x1 = []
    y1 = []
    if('coolStart' not in kwargs and 'coolEnd' not in kwargs):
        for i in range(temp, temp1 + 1):
            x1.append(x0[i])
            y1.append(y0[i])
    elif('coolStart' in kwargs and 'coolEnd' in kwargs):
        for i in range(len(x)):
            if(abs(x[i]-kwargs['coolStart'])<0.001):
                flag1=i
                break
        for i in range(len(x)):
            if(abs(x[i]-kwargs['coolEnd'])<0.001):
                flag2=i
                break
        for i in range(flag1, flag2+ 1):
            x1.append(x0[i])
            y1.append(y0[i])
    else:
        if("coolStart" in kwargs):
            for i in range(len(x)):
                if(abs(x[i]-kwargs["coolStart"])<0.01):
                    flag=i
                    break
            for i in range(flag,temp1+1):
                x1.append(x0[i])
                y1.append(y0[i])
            print('correct')
            print(x0[flag], y0[flag])
            print(x0[temp1], y0[temp1])
        else:
            for i in range(len(x)):
                if(abs(x[i]-kwargs["coolEnd"])<0.01):
                    flag=i
                    break
            for i in range(temp,flag+1):
                x1.append(x0[i])
                y1.append(y0[i])
    print(x1[0],x1[-1])
    return x1,y1

if __name__ == '__main__':
    filename = '../static/file/20180921185434冷却曲线.csv'
    correct(filename,coolEnd=124.906,coolStart=80.3982)