from scipy import optimize, math
from app import getXt1AndXt2

def f(x,a,b):
    return a*x+b

# 步骤1，对升温数据进行基线修正
def correctHot(filename,**kwargs):
    x0, y0 = getXt1AndXt2.readCsv(filename)
    miny = y0.index(min(y0))  # 最低温度点
    x = []
    y = []
    for i in range(len(y0)):
        y.append(-y0[i] / y0[miny] * 100)
        x.append(x0[i])

    # 用来寻找终点b
    count = 0
    for i in range(len(x)):
        count = count + 1  # count为5℃所包含的数据点
        if x[i] - x[0] >= 5:
            break

    # 剔除升温数据温度最后5℃包含的数据点
    for i in range(miny, len(x) - count, 1):
        xx = [x[i], x[i + count]]
        yy = [y[i], y[i + count]]
        a, b = optimize.curve_fit(f, xx, yy)[0]
        angle = math.atan(a) * 180 / math.pi  # 将斜率转换为角度
        # print("%f-%f:%f" % (x[i], x[i+count], angle))
        if angle < 5:  # 如果角度小于5，取该点为终点
            temp1 = i
            break

    # 用来寻找起点a
    ang = []
    # 去掉升温数据温度开始5℃的数据点
    for i in range(miny, count + 1, -1):
        xx = [x[i - count], x[i]]
        yy = [y[i - count], y[i]]
        a, b = optimize.curve_fit(f, xx, yy)[0]
        angle = math.atan(a) * 180 / math.pi
        ang.append(angle)
        # print("%f-%f:%f"%(x[i-count],x[i],angle))
    maxAng = max(ang)
    for i in range(len(ang)):
        if ang[i] == maxAng:
            temp = miny - i  # 两个数据之间的位置换算
            break
    # 在ab之间的点，存入x,y中
    # print('correct')
    # print(x[temp], y[temp])
    # print(x[temp1], y[temp1])
    x1 = []
    y1 = []

    if('heatStart' not in kwargs and 'heatEnd' not in kwargs):
        for i in range(temp, temp1 + 1):
            x1.append(x0[i])
            y1.append(y0[i])
    elif('heatStart' in kwargs and 'heatEnd' in kwargs):
        for i in range(len(x)):
            if (abs(x[i] - kwargs['heatStart']) < 0.001):
                flag1 = i
                break
        for i in range(len(x)):
            if (abs(x[i] - kwargs['heatEnd']) < 0.001):
                flag2 = i
                break
        for i in range(flag1, flag2 + 1):
            x1.append(x0[i])
            y1.append(y0[i])
    else:
        if ('heatStart' in kwargs):
            for i in range(len(x)):
                if (abs(x[i] - kwargs['heatStart']) < 0.01):
                    flag = i
                    break
            for i in range(flag, temp1 + 1):
                x1.append(x0[i])
                y1.append(y0[i])
        else:
            for i in range(len(x)):
                if (abs(x[i] - kwargs['heatEnd']) < 0.01):
                    flag = i
                    break
            for i in range(temp, flag + 1):
                x1.append(x0[i])
                y1.append(y0[i])
    return x1, y1

#步骤3，求Tm（计算Mn和Mw时使用的不同）
#步骤3.1，计算基线修正后的温度的平均温度（Mn）
def getAverageTm(filename,**kwargs):
    x=correctHot(filename,**kwargs)[0]
    sum=0
    for i in range(len(x)):
        sum=sum+x[i]
    Tm=sum/len(x)
    return Tm

#3.2，求出纵坐标乘以横坐标除以纵坐标之和作为平均温度（Mw）
def getTmOfMw(filename,**kwargs):
    x,y=correctHot(filename,**kwargs)
    sum=0
    sum1=0
    for i in range(len(x)):
        sum=x[i]*abs(y[i])+sum
        sum1=abs(y[i])+sum1
    tm=sum/sum1
    return tm


if __name__ == '__main__':
    filename = 'C:/Users/LFK/Desktop/数据/数据/输入数据2-升温曲线.csv'
    # filename = 'C:/Users/LFK/Desktop/数据/数据/MPEO 21k 16C heating.csv'
    # filename= 'C:/Users/LFK/Documents/WeChat Files/LFK613/Files/PP F401 heating after 10K-min.csv'
    correctHot(filename)
    average=getAverageTm(filename)
    print('average:%f'%average)
    tm=getTmOfMw(filename)
    print('tm:%f' % tm)