from myflask.main import getXt1AndXt2


#改文件为升温数据文件，对应于前端的file3
#导入csv文件
def correctHot(filename):
    x0, y0 = getXt1AndXt2.readCsv(filename)
    # 用来找到终点b，暂定斜率和平行线误差在0.001内,选取温度大于150度，确保之前的数据有误差，差生的斜率大于0
    for index in range(len(x0)):
        xx = (x0[index + 1] - x0[index]) / 10
        yy = y0[index + 1] - y0[index]
        k = yy / xx
        if x0[index] > 150 and k > 0 and abs(k - 0) < 0.001:
            temp1 = index
            break

    # 用来寻找起点a，因为基线是和x轴平行，暂定b和a点y值相减误差在0.009以内
    for i in range(temp1 - 10):
        if (y0[i] - y0[temp1] < 0.009):
            temp = i
            break

    # 在ab之间的点，存入x,y中
    x = []
    y = []
    for j in range(temp, temp1 + 1):
        x.append(x0[j])
        y.append(y0[j])
    return x,y

#求出升温曲线的熔融焓
def getHotHm(filename):
    y=correctHot(filename)[1]
    deltaHm=0.0
    for i in range(len(y)):
        flag=abs(y[i])-abs(y[0])
        deltaHm=deltaHm+flag
    return deltaHm

#求出纵坐标最大的横坐标
def getXofmaxy(filename):
    x,y=correctHot(filename)
    index=y.index(min(y))
    maxX=x[index]
    return maxX


if __name__ == '__main__':
    filename = 'C:/Users/LFK/Desktop/数据/数据/输入数据2-升温曲线.csv'
    Hm=getHotHm(filename)