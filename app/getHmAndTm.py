from scipy import optimize, math
from app import getXt1AndXt2

def f(x,a,b):
    return a*x+b
def correctHot(filename):
    x,y = getXt1AndXt2.readCsv(filename)
    miny = y.index(min(y))
    # 用来找到终点b,因为这点曲线比较平缓
    count=0
    for i in range(len(x)):
        count = count + 1
        if x[i] - x[0] >=5:
            break
    for i in range(len(x)):
        if x[i] - x[miny] >= 10:
            start1=i
            break
    for i in range(start1, len(x) - count, 1):
        xx = [x[i], x[i + count]]
        yy = [y[i], y[i + count]]
        a, b = optimize.curve_fit(f, xx, yy)[0]
        k = abs(a)
        if k < math.tan(1 * math.pi / 180):
            temp1 = i
            break

    for i in range(miny):
        if abs(y[i]-y[temp1])<0.01:
            temp=i
    # 在ab之间的点，存入x,y中
    # print('correct')
    # print(x[temp], y[temp])
    # print(x[temp1], y[temp1])
    x1 = []
    y1 = []
    for i in range(temp, temp1 + 1):
        x1.append(x[i])
        y1.append(y[i])
    return x1, y1

#求出升温曲线的熔融焓
def getHotHm(filename):
    y=correctHot(filename)[1]
    deltaHm=0.0
    for i in range(len(y)):
        flag=abs(y[i])-abs(y[0])
        deltaHm=deltaHm+flag
    return deltaHm

def getAverageTm(filename):
    x=correctHot(filename)[0]
    sum=0
    for i in range(len(x)):
        sum=sum+x[i]
    Tm=sum/len(x)
    return Tm


#求出纵坐标最大的横坐标
def getMaxTm(filename):
    x,y=correctHot(filename)
    index=y.index(min(y))
    Tm=x[index]
    return Tm


if __name__ == '__main__':
    filename = 'C:/Users/LFK/Desktop/数据/数据/输入数据2-升温曲线.csv'
    filename1 = 'C:/Users/LFK/Desktop/数据/数据/MPEO 21k 16C heating.csv'
    average=getAverageTm(filename)
    max=getMaxTm(filename)
    print('average:%f'%average)
    print('max:%f'%max)