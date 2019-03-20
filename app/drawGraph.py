from app import getHmAndTm, getXt1AndXt2
from pylab import *
import os
#图标用中文显示
mpl.rcParams['font.sans-serif'] = ['SimHei']
#图标显示负号
matplotlib.rcParams['axes.unicode_minus']=False

tmp = 'static/image'
curdir = os.path.abspath('.')  # 获得当前工作目录,如果在加一个点，是获得当前目录的父目录
savefold= curdir + os.path.altsep + tmp + os.path.altsep  # 该路径为当前文件夹拼接windows下文件分隔符再拼接'tmp'文件夹，再拼接文件分隔符
if os.path.exists(savefold) == False:
    os.makedirs(savefold)

#1.绘制降温曲线
def coolGraph(filename,str):
    htext='原始降温曲线'
    xtext='Temperature(℃)'
    ytext='Heatflow(a.u.)'
    x,y=getXt1AndXt2.readCsv(filename)
    cpValue='blue'
    ptext='降温曲线'
    drawPlot(htext, xtext, ytext, x, y, cpValue, ptext,str)

#2.绘制基线修正后的降温曲线
def coolCorrectGraph(filename,str):
    x, y = getXt1AndXt2.correct(filename)
    xx=[x[0],x[len(x)-1]]
    yy=[y[0],y[len(x)-1]]
    cjValue='red'
    pjtext='基线'
    plt.plot(xx,yy,c=cjValue,label=pjtext)
    htext = '基线修正后降温曲线'
    xtext = 'Temperature(℃)'
    ytext = 'Heatflow(a.u.)'
    cpValue = 'blue'
    ptext = '降温曲线'
    drawPlot(htext, xtext, ytext, x, y, cpValue, ptext, str)

#2.1绘制热流量和时间的曲线
def coolTGraph(filename,str):
    x= getXt1AndXt2.temperatureToTime(filename)
    y= getXt1AndXt2.correct(filename)[1]
    htext = '基线修正后热流量-时间曲线'
    xtext = 'Temperature(℃)'
    ytext = 'Heatflow(a.u.)'
    cpValue = 'blue'
    ptext = '热流量-时间曲线'
    drawPlot(htext, xtext, ytext, x, y, cpValue, ptext, str)


#3.绘制相对结晶度随时间变化的曲线
def xtWithTGraph(filename,str):
    htext = '降温：相对结晶度—时间图像'
    xtext = 'Time/min'
    ytext = 'Xt'
    x= getXt1AndXt2.temperatureToTime(filename)
    y= getXt1AndXt2.caculateXt(filename)
    cpValue = 'blue'
    ptext = '相对结晶度—时间'
    drawPlot(htext, xtext, ytext, x, y, cpValue, ptext,str)

#4.绘制相对结晶度随温度变化的曲线
def xtWithTemperatureGraph(filename,str):
    htext = '降温：相对结晶度—温度图像'
    xtext = 'Temperature(℃)'
    ytext = 'Xt'
    x = getXt1AndXt2.correct(filename)[0]
    y = getXt1AndXt2.caculateXt(filename)
    cpValue = 'blue'
    ptext = '相对结晶度—温度'
    drawPlot(htext, xtext, ytext, x, y, cpValue, ptext,str)

#5.绘制ln(-ln(1-xt))关于lntr的曲线,其中tr=t/t总
def trWithxtGraph(filename,str):
    htext = 'ln(-ln(1-Xt))关于lntr的图像'
    xtext = 'ln(t/t总）'
    ytext = 'ln(-ln(1-Xt))'
    x,y = getXt1AndXt2.changeTAndXt(filename)
    cpValue = 'cyan'
    ptext = 'ln(-ln(1-Xt))—lntr'
    drawPlot(htext, xtext, ytext, x, y, cpValue, ptext,str)

#6.绘制升温曲线
def hotGraph(filename,str):
    htext = '原始升温曲线'
    xtext = 'Temperature(℃)'
    ytext = 'Heatflow(a.u.)'
    x,y= getXt1AndXt2.readCsv(filename)
    cpValue = 'red'
    ptext = '升温曲线'
    drawPlot(htext, xtext, ytext, x, y, cpValue, ptext,str)

#7.绘制基线修正后的升温曲线
def hotCorrectGraph(filename,str):
    x,y= getHmAndTm.correctHot(filename)
    xx = [x[0], x[len(x) - 1]]
    yy = [y[0], y[len(x)-1]]
    cjValue = 'blue'
    pjtext = '基线'
    plt.plot(xx, yy, c=cjValue, label=pjtext)
    htext = '基线修正后升温曲线'
    xtext = 'Temperature(℃)'
    ytext = 'Heatflow(a.u.)'
    cpValue = 'red'
    ptext = '升温曲线'
    drawPlot(htext, xtext, ytext, x, y, cpValue, ptext, str)

#8.绘制拟合直线求交点的图像
def profitFindSecondPointGraph(filename,str):
    x6,y6= getXt1AndXt2.getFirstProfitPoint(filename)
    plt.scatter(x6[:], y6[:], 25, 'yellow')
    x1,y1= getXt1AndXt2.getFirstLinePoint(filename)
    plt.plot(x1, y1, 'blue', label='[-5,-3]的拟合直线')
    x7,y7= getXt1AndXt2.getSecondProfitPoint(filename)
    plt.scatter(x7[:], y7[:], 25, 'green')
    x2,y2= getXt1AndXt2.getSecondLinePoint(filename)
    plt.plot(x2, y2, 'red', label='[-1.6,-1.1]的拟合直线')
    x,y= getXt1AndXt2.getPointOfIntersection(filename)
    plt.scatter(x, y, 25, 'black', label=(x, y))
    htext = '求交点图像'
    xtext = 'ln(t/t总）'
    ytext = 'ln(-ln(1-Xt))'
    x, y = getXt1AndXt2.changeTAndXt(filename)
    cpValue = 'cyan'
    ptext = 'ln(-ln(1-Xt))—lntr'
    drawPlot(htext, xtext, ytext, x, y, cpValue, ptext, str)

#9,一次绘制所有图像
def drawAllGraph(f1,f2):
    coolGraph(f1, '降温曲线')
    hotGraph(f2, '升温曲线')
    coolCorrectGraph(f1,'基线修正后降温曲线')
    hotCorrectGraph(f2, '基线修正后升温曲线')
    coolTGraph(f1,'热流量-时间曲线')
    xtWithTemperatureGraph(f1, '降温：相对结晶度—温度')
    xtWithTGraph(f1,'降温：相对结晶度—时间')
    trWithxtGraph(f1,'ln(-ln(1-Xt))关于lntr的图像')
    profitFindSecondPointGraph(f1, '求交点图像')

#绘图
def drawPlot(htext,xtext,ytext,x,y,cpValue,ptext,str):
    plt.title(htext,fontsize=24)
    plt.xlabel(xtext,fontsize=16)
    plt.ylabel(ytext,fontsize=16)
    plt.plot(x,y,c=cpValue,label=ptext)
    plt.legend()
    plt.grid(True)
    imagename=str+'2.jpg'
    # plt.savefig(savefold+imagename)
    plt.show()

if __name__ == '__main__':
    # f1= 'C:/Users/LFK/Desktop/数据/数据/输入数据1-冷却曲线.csv'
    # f2 = 'C:/Users/LFK/Desktop/数据/数据/输入数据2-升温曲线.csv'
    # f1='C:/Users/LFK/Desktop/数据/数据/MPEO 21k 16C cooling.csv'
    # f2= 'C:/Users/LFK/Desktop/数据/数据/MPEO 21k 16C heating.csv'
    # f1= 'C:/Users/LFK/Documents/WeChat Files/LFK613/Files/PP F401 10K-min cooling.csv'
    # f2 = 'C:/Users/LFK/Documents/WeChat Files/LFK613/Files/PP F401 heating after 10K-min.csv'
    # f1='C:/Users/LFK/Desktop/PP LWM/冷却曲线.csv'
    # f2='C:/Users/LFK/Desktop/PP LWM/升温曲线.csv'
    f1 = 'C:/Users/LFK/Desktop/PP LWM/输入数据1-冷却曲线.csv'
    f2 = 'C:/Users/LFK/Desktop/PP LWM/输入数据2-升温曲线.csv'
    drawAllGraph(f1,f2)

