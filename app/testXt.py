import csv
from operator import itemgetter

import  numpy as np
import math
import copy
#图标用中文显示
from scipy import optimize

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
def correct(filename):
    x,y=readCsv(filename)
    # 用来寻找终点b
    count=0
    for i in range(len(x)):
        count=count+1
        if x[i]-x[0]>=5:
            break

    maxy = y.index(max(y))
    for i in range(len(x)):
        if x[i] - x[maxy] >= 5:
            start1 = i
            break

    for i in range(start1, len(x)-11,1):
        xx = [x[i], x[i + count]]
        yy = [y[i], y[i + count]]
        a, b = optimize.curve_fit(f, xx, yy)[0]
        k = abs(a)
        if k < math.tan(1* math.pi / 180):
            temp1 = i
            break

    # 用来找到a点起点，暂定斜率为10度
    for i in range(len(x)):
        if x[maxy] - x[i] <= 5:
            start = i
            break

    for i in range(len(x)):
        if x[i] - x[0] >= 10:
            end = i
            break

    for i in range(start, end, -1):
        xx = [x[i], x[i -count]]
        yy = [y[i], y[i -count]]
        a, b = optimize.curve_fit(f, xx, yy)[0]
        k = abs(a)
        if k < math.tan(1 * math.pi / 180):
            temp = i
            break

    # 在ab之间的点，存入x,y中
    print('correct')
    print(x[temp], y[temp])
    print(x[temp1], y[temp1])
    x1 = []
    y1 = []
    for i in range(temp, temp1 + 1):
        x1.append(x[i])
        y1.append(y[i])
    return x1,y1

# 步骤3，求相对结晶度Xt，存在y4中，降序排列(因为求的基线不是近似平行的，所以求直线积分，然后减去）
def caculateXt(filename):
    x, y = correct(filename)
    # 拟合后的直线方程
    xx = [x[0], x[len(x) - 1]]
    yy = [y[0], y[len(y) - 1]]
    a,b = optimize.curve_fit(f, xx, yy)[0]
    y1=[]
    for i in range(len(x)):
        y1.append(a*x[i]+b)
    area=np.trapz(y,x)-np.trapz(y1,x)
    x11=[]
    y11=[]
    y12=[]
    Xt=[]
    for i in range(len(x)):
        x11.append(x[i])
        y11.append(y[i])
        y12.append(y1[i])
        area1=np.trapz(y11,x11)-np.trapz(y12,x11)
        area2=abs(area)-abs(area1)
        Xt.append(area2/area)   #相对结晶度从1到0存储
    return Xt

if __name__ == '__main__':
    filename = 'C:/Users/LFK/Desktop/数据/数据/输入数据1-冷却曲线.csv'
    filename1='C:/Users/LFK/Desktop/数据/数据/MPEO 21k 16C cooling.csv'
    # correct(filename1)
    xt=caculateXt(filename1)
    print(xt)