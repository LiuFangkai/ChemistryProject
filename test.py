import csv
from operator import itemgetter
from scipy import optimize, math
import  numpy as np
import math
import copy
#图标用中文显示
from scipy import optimize
import os
from flask import render_template
from flask import Flask, request

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
    # print('correct')
    # print(x[temp], y[temp])
    # print(x[temp1], y[temp1])
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
        if x5[i] >= -2 and x5[i] <= -1:  # 因为x5中是从小到大排序的，都是小于0的，因此第一个找到的点即近似分离点
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

# 6.4求[-5,-3]和[-2.2,-1]两直线的交点
def getPointOfIntersection(filename,v):
    a1,b1=getFirstLine(filename,v)
    a2,b2=getSecondLine(filename,v)
    x = (b1 - b2) / (a2 - a1)
    y = a1 * x + b1
    return x,y

# #x0从大到小，y0从小到大
# def getY2(filename,v):
#     x0,y0=changeTAndXt(filename,v)
#     x,y=getPointOfIntersection(filename,v)
#     for i in range(len(x0)):
#         if x==x0[i]:  #如果存在x的值和x0[i]相等，则直接令x对的y值为x0[i]这一点的纵坐标值
#             y2=y0[i]
#         elif x>x0[i]:  #否则，去x对应的y值为介于x两边的纵坐标值的平均值
#             y2=(y0[i]+y0[i-1])/2
#             break
#     return y2
#
# def getXt2(filename,v):
#     y=getY2(filename,v)
#     Xt2 = 1 - math.exp(-math.exp(y))
#     return Xt2
#
# def getXt1(filename,v):
#     y=getPointOfIntersection(filename,v)[1]
#     Xt1=1 - math.exp(-math.exp(y))
#     return Xt1

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

def getXt2(filename,v):
    y=getPointOfIntersection(filename,v)[1]
    Xt2 = 1 - math.exp(-math.exp(y))
    return Xt2


#计算Tm和Hm
def f(x,a,b):
    return a*x+b
def correctHot(filename):
    x,y =readCsv(filename)
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

#计算Mn，Mw和PDI
#filename为升温数据的,Tm为所有温度的平均值
def getMn(Xt2,filename,Lu, Mo, pc, deltaHm0, sigmae, Tm0):
    deltaHm2 =getHotHm(filename) * getHotHm(filename)
    Tm=getAverageTm(filename)
    fz=2*sigmae*deltaHm0*Mo  #分子
    fm = deltaHm2 * Xt2 * Lu * pc * (1 - Tm / Tm0)
    Mn=fz/fm
    return Mn

def getMw(Xt1,Xt2,filename,Lu, Mo, pc, deltaHm0, sigmae, Tm0):
    deltaHm2 =getHotHm(filename) * getHotHm(filename)
    Tm = getMaxTm(filename)
    fz = 2 * sigmae * deltaHm0 * Mo  # 分子
    fm = deltaHm2 * Xt1 * Lu * pc * (1 - Tm / Tm0)
    fm1= deltaHm2 * Xt2 * Lu * pc * (1 - Tm / Tm0)
    Mi1 = fz / fm
    Mi2=fz/fm1
    Mw=(Mi1+Mi2)/2
    return Mw

def getPDI(Mn,Mw):
    PDI=Mw/Mn
    return PDI

#和前端对应,file2为降温曲线，file3为升温曲线
def getAlldata(filename2,filename3,v,Lu, Mo, pc, deltaHm0, sigmae, Tm0):
    xt1=getXt1(filename2,v)
    xt2=getXt2(filename2, v)
    Mn=getMn(xt2, filename3, Lu, Mo, pc, deltaHm0, sigmae, Tm0)
    Mw=getMw(xt1,xt2, filename3, Lu, Mo, pc, deltaHm0, sigmae, Tm0)
    PDI=getPDI(Mn,Mw)
    return Mn,Mw,PDI



ALLOWED_EXTENSIONS = set(['txt','csv'])
#python3自动生成文件名
from datetime import *

tmp = 'static/file'
curdir = os.path.abspath('.')  # 获得当前工作目录,如果在加一个点，是获得当前目录的父目录
UPLOAD_FOLDER = curdir + os.path.altsep + tmp + os.path.altsep  # 该路径为当前文件夹拼接windows下文件分隔符再拼接'tmp'文件夹，再拼接文件分隔符
if os.path.exists(UPLOAD_FOLDER) == False:
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#高分子数据(Lu,Mo,pc,deltaHm0,sigmae,Tm0)
#(结构单元长度nm，结构单元分子量，晶区密度，完美熔融焓，表面能，平衡熔点k)
#JBX:聚丙烯  PEO:聚氧化乙烯
JBXData=[0.2167,42,0.936,209.2,30,459-273.15]
PEOData=[0.2783,44,1.228,220,31,69]

def getData(arr):
    Lu=float(arr[0])
    Mo=float(arr[1])
    pc=float(arr[2])
    deltaHm0=float(arr[3])
    sigmae=float(arr[4])
    Tm0=float(arr[5])
    return Lu,Mo,pc,deltaHm0,sigmae,Tm0


#用来判断上传的文件是否是csv文件
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#生成唯一的文件名
def randomfile(filename):
    nowTime =datetime.now().strftime("%Y%m%d%H%M%S")  # 生成当前的时间
    uniqueNum=str(nowTime)
    uniqueFile=uniqueNum+filename
    return uniqueFile

#下载单个文件,返回改文件的路径
def upload_single_file(label):
    file = request.files[label]
    if file and allowed_file(file.filename):
        filename = randomfile(file.filename)
        uploadpath=os.path.join(app.config['UPLOAD_FOLDER'], filename).replace('\\','/')
        file.save(uploadpath)
    return uploadpath

#返回所有文件的路径
def upload_all_file():
    uploadpath2 = upload_single_file('file2')
    uploadpath3 = upload_single_file('file3')
    return uploadpath2,uploadpath3

#计算所得到的值，并返回
def caculate():
    path2,path3=upload_all_file()
    v=int(request.form.get('velocity'))  #获取前台的v值
    if request.form.get("select") == 'JuBingXi':  #获取前台select中选中的value值
        Lu, Mo, pc, deltaHm0, sigmae, Tm0 = getData(JBXData)
    if request.form.get("select") == 'JuYangHuaYiXi':
        Lu, Mo, pc, deltaHm0, sigmae, Tm0 = getData(JBXData)
    Mn,Mw,PDI=getAlldata(path2, path3, v, Lu, Mo, pc, deltaHm0, sigmae, Tm0)
    return Mn,Mw,PDI

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        Mn,Mw,PDI=caculate()
        data={
            'Mn':Mn,
            'Mw':Mw,
            'PDI':PDI
        }
        return render_template('result.html',data=data)
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')