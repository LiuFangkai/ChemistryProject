import csv
from operator import itemgetter

import  numpy as np
import math
import copy
#图标用中文显示
from scipy import optimize


#该文件为降温数据文件，对应于前端file2

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

#步骤2，进行基线修正，确定a，b两点，返回修正后的坐标，存在x，y中
def correct(filename):
    x1,y1=readCsv(filename)
    # 用来找到a点起点，暂定斜率为10度
    for i in range(len(x1)):
        xx = (x1[i + 1] - x1[i]) / 10
        yy = y1[i + 1] - y1[i]
        k = yy / xx
        if k > math.tan(10 * math.pi / 180) and x1[i] > 60:
            temp = i
            break

    # 用来寻找终点b，因为基线是和x轴平行，暂定b和a点y值相减误差在0.009以内
    for i in range(temp + 10, len(x1)):
        if (y1[i] - y1[temp] < 0.01):
            temp1 = i
            break

    # 在ab之间的点，存入x,y中
    x = []
    y = []
    for j in range(temp, temp1 + 1):
        x.append(x1[j])
        y.append(y1[j])
    return x,y

#步骤3，求相对结晶度Xt，存在y4中，降序排列
def caculateXt(filename):
    x=correct(filename)[0]
    y=correct(filename)[1]
    # 和基线围成的积分面积
    area1 = np.trapz(y, x)
    area2 = y[0] * (x[len(x)-1]-x[0])
    area = area1 - area2
    # 求相对结晶度Xt（积分面积占总面积比例）
    x3 = []
    y3 = []
    y4 = []
    for m in range(len(x)):
        x3.append(x[m])
        y3.append(y[m])
        tempArea1 = np.trapz(y3, x3)
        tempArea2 = y[0] * (x[m] - x[0])
        tempArea3 = tempArea1 - tempArea2
        tempArea = area - tempArea3
        y4.append(tempArea / area)
    return y4

#步骤4，将温度变化从b-a转化成从b-a所用的时间，降序排列的，存在x2中,
# !!!!注意，因为下面用的是部分时间与总时间的比例，所以降温速度为多少，并不影响最后结果
def temperatureToTime(filename,v):
    x=correct(filename)[0]
    # x2中存储温度变化时间，降序（b-a到b-b）
    x2 = []
    for k in range(len(x)):
        x2.append(abs(x[len(x) - 1] - x[k]) / v)
    return x2

#步骤5，计算经转化后的t，Xt，存在x5，y5中
    # 横坐标为In(t/t总)，存在x5中
    # 从大到小，纵坐标为ln(-ln(1-Xt))，存在y5中
def changeTAndXt(filename,v):
    x2=temperatureToTime(filename,v)
    y4=caculateXt(filename)
    x5 = []
    y5 = []
    totalTime = x2[0]
    for i in range(1, len(x2) - 1):  # x2中最后一个元素为0，不能做分母，排除
        tr = x2[i] / totalTime
        x5.append(math.log(tr))
    for i in range(1, len(y4) - 1):  # y4中第一个元素为1，最后一个元素为0，不能放在log里面，排除
        y5.append(math.log(-(math.log(1 - y4[i]))))
    return x5,y5

#步骤6，进行曲线拟合，求交点

#6.1待拟合的两条线为直线
def f(x,a,b):
    return a*x+b

# 6.2进行-5到-3之间的直线拟合
#6.2.1找到符合条件的第一条直线的离散点
def getFirstProfitPoint(filename,v):
    x5 = changeTAndXt(filename,v)[0]
    y5 = changeTAndXt(filename,v)[1]
    x6 = []
    y6 = []
    for i in range(len(x5)):
        if x5[i] >= -5 and x5[i] <= -3:
            x6.append(x5[i])
            y6.append(y5[i])
    return x6,y6
#6.2.2根据离散点进行线性拟合，求出第一条直线方程
def getFirstLine(filename,v):
    x6,y6=getFirstProfitPoint(filename,v)
    a1, b1 = optimize.curve_fit(f, x6, y6)[0]
    return a1,b1
#6.2.3根据拟合求出来的第一条直线方程，取出若干对x，y
def getFirstLinePoint(filename,v):
    a1,b1=getFirstLine(filename,v)
    x = np.arange(-5,0, 0.01)
    y = a1 * x + b1
    return x,y

# 6.3进行-2.2到-1之间的直线拟合
#6.3.1找到符合条件的第二条直线的离散点
def getSecondProfitPoint(filename,v):
    x5 = changeTAndXt(filename,v)[0]
    y5 = changeTAndXt(filename,v)[1]
    x7 = []
    y7 = []
    for i in range(len(x5)):
        if x5[i] >= -2.2 and x5[i] <= -1:  # 因为x5中是从小到大排序的，都是小于0的，因此第一个找到的点即近似分离点
            x7.append(x5[i])
            y7.append(y5[i])
    return x7,y7
#6.3.2根据离散点进行线性拟合，求出第二条直线方程
def getSecondLine(filename,v):
    x7,y7=getSecondProfitPoint(filename,v)
    a2, b2 = optimize.curve_fit(f, x7, y7)[0]
    return a2,b2
#6.3.3根据拟合求出来的第二条直线方程，取出若干对x，y
def getSecondLinePoint(filename,v):
    a2,b2=getSecondLine(filename,v)
    x = np.arange(-4, 0, 0.01)
    y = a2 * x + b2
    return x,y

# 6.4求[-5,-3]和[-2.2,-1]两直线的交点(即第二个交点)
def getSecondPoint(filename,v):
    a1,b1=getFirstLine(filename,v)
    a2,b2=getSecondLine(filename,v)
    x = (b1 - b2) / (a2 - a1)
    y = a1 * x + b1
    return x,y
#6.4.1把交点对应的y值转换为相应的Xt
def getXt2(filename,v):
    y=getSecondPoint(filename,v)[1]
    Xt2 = 1 - math.exp(-math.exp(y))
    return Xt2

#6.5求第一个交点
#6.5.1选取ln(-ln(1-Xt))—lntr图像中的后十个点离散点
def getTenPoint(filename,v):
    x5, y5 = changeTAndXt(filename,v)
    x9 = []
    y9 = []
    for i in range(len(x5) - 1, len(x5) - 11, -1):
        x9.append(x5[i])
        y9.append(y5[i])
    return x9, y9
#6.5.2对10个离散点进行非线性拟合，求出函数表达式
def getTenPointLine(filename,v):
    x9,y9=getTenPoint(filename,v)
    z1 = np.polyfit(x9, y9, 4)  # 用3次多项式拟合
    p1 = np.poly1d(z1)
    return p1
#6.5.3找出拟合曲线的在某区间中的若干对x,y
def getPointProfitTenPoint(filename,v):
    p1 = getTenPointLine(filename,v)
    x= np.arange(-3.8, -3, 0.001)
    y=[]
    for i in range(len(x)):
        y.append(p1(x[i]))
    return x,y

#求拟合之后曲线的导数
def getDiff(filename,v):
    p=getTenPointLine(filename,v)
    p1=p.deriv()
    return p1
#6.5.4找出直线和曲线导数相近的点,y1是曲线，y2是直线
def getFirstPoint(filename,v):
    a1,b1=getFirstLine(filename,v)
    k2=a1
    y1=getDiff(filename,v)
    x1=np.arange(-5, -3, 0.01)
    for i in range(len(x1)):
        k1=y1(x1[i])
        if (k1-k2)<0.01 and (k1-k2)>0:
            xx=x1[i]
            yy = a1 * xx + b1
            break
    return xx,yy

 #把对应的y值转换成Xt1
def getXt1(filename,v):
    y=getFirstPoint(filename,v)[1]
    Xt1 = 1 - math.exp(-math.exp(y))
    return Xt1

if __name__ == '__main__':
    filename = 'C:/Users/LFK/Desktop/数据/数据/输入数据1-冷却曲线.csv'
    v=20
    # x2=temperatureToTime(filename,v)
    Xt2=getXt2(filename,v)
    print(Xt2)
    Xt1=getXt1(filename,v)
    print(Xt1)
    getDiff(filename,v)