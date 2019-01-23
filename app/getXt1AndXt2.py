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
        else:
            for i in range(len(x)):
                if(abs(x[i]-kwargs["coolEnd"])<0.01):
                    flag=i
                    break
            for i in range(temp,flag+1):
                x1.append(x0[i])
                y1.append(y0[i])
    return x1,y1

# 步骤3，求相对结晶度Xt，存在y4中，降序排列(因为求的基线不是近似平行的，所以求直线积分，然后减去）
def caculateXt(filename,**kwargs):
    x, y = correct(filename,**kwargs)
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

#步骤4，将温度变化从b-a转化成从b-a所用的时间，降序排列的，存在x2中,
# !!!!注意，因为下面用的是部分时间与总时间的比例，所以降温速度为多少，并不影响最后结果
def temperatureToTime(filename,**kwargs):
    x=correct(filename,**kwargs)[0]
    # x2中存储温度变化时间，降序（b-a到b-b）
    x2 = []
    for k in range(len(x)):
        x2.append(abs(x[len(x) - 1] - x[k]) / v)
    return x2

#步骤5，计算经转化后的t，Xt，存在x5，y5中
    # 横坐标为In(t/t总)，存在x5中
    # 从大到小，纵坐标为ln(-ln(1-Xt))，存在y5中
def changeTAndXt(filename,**kwargs):
    x2=temperatureToTime(filename,**kwargs)
    y4=caculateXt(filename,**kwargs)
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
def getFirstProfitPoint(filename,**kwargs):
    global leftStart
    global leftEnd
    leftStart = -5
    leftEnd = -3
    if('leftStart' in kwargs and 'leftEnd' in kwargs):
        leftStart=kwargs['leftStart']
        leftEnd=kwargs['leftEnd']
    elif('leftStart' in kwargs and 'leftEnd' not in kwargs):
        leftStart = kwargs['leftStart']
    elif('leftStart' not in kwargs and 'leftEnd' in kwargs):
        leftEnd = kwargs['leftEnd']
    else:
        pass
    x5 = changeTAndXt(filename,**kwargs)[0]
    y5 = changeTAndXt(filename,**kwargs)[1]
    x6 = []
    y6 = []
    for i in range(len(x5)):
        if x5[i] >= leftStart and x5[i] <= leftEnd:
            x6.append(x5[i])
            y6.append(y5[i])
    return x6,y6
#6.2.2根据离散点进行线性拟合，求出第一条直线方程
def getFirstLine(filename,**kwargs):
    x6,y6=getFirstProfitPoint(filename,**kwargs)
    a1, b1 = optimize.curve_fit(f, x6, y6)[0]
    return a1,b1
#6.2.3根据拟合求出来的第一条直线方程，取出若干对x，y
def getFirstLinePoint(filename,**kwargs):
    a1,b1=getFirstLine(filename,**kwargs)
    x = np.arange(-5,0, 0.01)
    y = a1 * x + b1
    return x,y

# 6.3进行-1.6到-1.1之间的直线拟合
#6.3.1找到符合条件的第二条直线的离散点
def getSecondProfitPoint(filename,**kwargs):
    global rightStart
    rightStart = -1.6
    global rightEnd
    rightEnd = -1.1
    if('rightStart' in kwargs and 'rightEnd' in kwargs):
        rightStart=kwargs['rightStart']
        rightEnd=kwargs['rightEnd']
    elif('rightStart' in kwargs and 'rightEnd' not in kwargs):
        rightStart = kwargs['rightStart']
    elif('rightStart' not in kwargs and 'rightEnd' in kwargs):
        rightEnd = kwargs['rightEnd']
    else:
        pass

    x5 = changeTAndXt(filename,**kwargs)[0]
    y5 = changeTAndXt(filename,**kwargs)[1]
    x7 = []
    y7 = []
    for i in range(len(x5)):
        if x5[i] >= rightStart and x5[i] <= rightEnd:  # 因为x5中是从小到大排序的，都是小于0的，因此第一个找到的点即近似分离点
            x7.append(x5[i])
            y7.append(y5[i])
    return x7,y7
#6.3.2根据离散点进行线性拟合，求出第二条直线方程
def getSecondLine(filename,**kwargs):
    x7,y7=getSecondProfitPoint(filename,**kwargs)
    a2, b2 = optimize.curve_fit(f, x7, y7)[0]
    return a2,b2
#6.3.3根据拟合求出来的第二条直线方程，取出若干对x，y
def getSecondLinePoint(filename,**kwargs):
    a2,b2=getSecondLine(filename,**kwargs)
    x = np.arange(-4, 0, 0.01)
    y = a2 * x + b2
    return x,y

# 6.4求[-5,-3]和[-1.6,-1.1]两直线的交点
def getPointOfIntersection(filename,**kwargs):
    a1,b1=getFirstLine(filename,**kwargs)
    a2,b2=getSecondLine(filename,**kwargs)
    x = (b1 - b2) / (a2 - a1)
    y = a1 * x + b1
    return x,y

#步骤7，根据交点求出Xt1，Xt2
#步骤7.1，过交点做垂直于x轴的线，交于原曲线，求出此交点的y值（x0从大到小，y0从小到大）
def getY2(filename,**kwargs):
    x0,y0=changeTAndXt(filename,**kwargs)
    x,y=getPointOfIntersection(filename,**kwargs)
    for i in range(len(x0)):
        if x==x0[i]:  #如果存在x的值和x0[i]相等，则直接令x对的y值为x0[i]这一点的纵坐标值
            y2=y0[i]
        elif x>x0[i]:  #否则，去x对应的y值为介于x两边的纵坐标值的平均值
            y2=(y0[i]+y0[i-1])/2
            break
    return y2
#步骤7.2，由y2求出Xt2
def getXt2(filename,**kwargs):
    y=getY2(filename,**kwargs)
    Xt2 = 1 - math.exp(-math.exp(y))
    return Xt2
#步骤7.3，由步骤6中的交点中的y1求出Xt1
def getXt1(filename,**kwargs):
    y=getPointOfIntersection(filename,**kwargs)[1]
    Xt1=1 - math.exp(-math.exp(y))
    return Xt1


if __name__ == '__main__':
    filename = './static/file/20180921185434冷却曲线.csv'
    # filename = 'C:/Users/LFK/Desktop/数据/数据/MPEO 21k 16C cooling.csv'
    # filename = 'C:/Users/LFK/Documents/WeChat Files/LFK613/Files/PP F401 10K-min cooling.csv'
    xt1=getXt1(filename)
    xt2=getXt2(filename)
    print('Xt1:%f,Xt2:%f'%(xt1,xt2))