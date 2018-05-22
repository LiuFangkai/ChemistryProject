from cool import getXt1AndXt2
from hot import getHmAndTm
from matplotlib import pyplot as plt
from pylab import *
#图标用中文显示
mpl.rcParams['font.sans-serif'] = ['SimHei']
#图标显示负号
matplotlib.rcParams['axes.unicode_minus']=False
#绘图
def drawPlot(htext,xtext,ytext,x,y,cpValue,ptext):
    plt.title(htext,fontsize=24)
    plt.xlabel(xtext,fontsize=16)
    plt.ylabel(ytext,fontsize=16)
    plt.plot(x,y,c=cpValue,label=ptext)
    plt.legend()
    plt.grid(True)
    # plt.savefig('.jpg')
    plt.show()

#1.绘制降温曲线
def coolGraph(filename):
    htext='原始降温曲线'
    xtext='Temperature(℃)'
    ytext='Heatflow(a.u.)'
    x=getXt1AndXt2.changeDECtoASC(filename)[0]
    y=getXt1AndXt2.changeDECtoASC(filename)[1]
    cpValue='blue'
    ptext='降温曲线'
    drawPlot(htext, xtext, ytext, x, y, cpValue, ptext)

#2.绘制基线修正后的降温曲线
def coolCorrectGraph(filename):
    plt.title('基线修正后降温曲线')
    plt.xlabel('Temperature(℃)')
    plt.ylabel('Heatflow(a.u.)')
    x,y=getXt1AndXt2.correct(filename)
    cpValue='blue'
    ptext='降温曲线'
    plt.plot(x,y,c=cpValue,label=ptext)
    xx=[x[0],x[len(x)-1]]
    yy=[y[0],y[0]]
    cjValue='red'
    pjtext='基线'
    plt.plot(xx,yy,c=cjValue,label=pjtext)
    plt.legend()
    plt.grid()
    plt.show()

#3.绘制相对结晶度随时间变化的曲线
def xtWithTGraph(filename):
    htext = '降温：相对结晶度—时间图像'
    xtext = 'Time/min'
    ytext = 'Xt'
    x=getXt1AndXt2.temperatureToTime()
    y=getXt1AndXt2.caculateXt()
    cpValue = 'blue'
    ptext = '相对结晶度—时间'
    drawPlot(htext, xtext, ytext, x, y, cpValue, ptext)

#4.绘制相对结晶度随温度变化的曲线
def xtWithTemperatureGraph(filename):
    htext = '降温：相对结晶度—温度图像'
    xtext = 'Temperature(℃)'
    ytext = 'Xt'
    x = getXt1AndXt2.correct(filename)[0]
    y = getXt1AndXt2.caculateXt(filename)
    cpValue = 'blue'
    ptext = '相对结晶度—温度'
    drawPlot(htext, xtext, ytext, x, y, cpValue, ptext)

#5.绘制ln(-ln(1-xt))关于lntr的曲线,其中tr=t/t总
def trWithxtGraph(filename):
    htext = 'ln(-ln(1-Xt))关于lntr的图像'
    xtext = 'ln(t/t总）'
    ytext = 'ln(-ln(1-Xt))'
    x,y = getXt1AndXt2.changeTAndXt(filename)
    cpValue = 'cyan'
    ptext = 'ln(-ln(1-Xt))—lntr'
    drawPlot(htext, xtext, ytext, x, y, cpValue, ptext)

#6.绘制升温曲线
def hotGraph(filename):
    htext = '原始升温曲线'
    xtext = 'Temperature(℃)'
    ytext = 'Heatflow(a.u.)'
    x,y=getHmAndTm.correctHot(filename)
    cpValue = 'red'
    ptext = '升温曲线'
    drawPlot(htext, xtext, ytext, x, y, cpValue, ptext)

#7.绘制基线修正后的升温曲线
def hotCorrectGraph(filename):
    plt.title('基线修正后升温曲线')
    plt.xlabel('Temperature(℃)')
    plt.ylabel('Heatflow(a.u.)')
    x,y=getHmAndTm.correctHot(filename)
    cpValue = 'red'
    ptext = '升温曲线'
    plt.plot(x, y, c=cpValue, label=ptext)
    xx = [x[0], x[len(x) - 1]]
    yy = [y[0], y[0]]
    cjValue = 'blue'
    pjtext = '基线'
    plt.plot(xx, yy, c=cjValue, label=pjtext)
    plt.legend()
    plt.grid()
    plt.show()

#8.绘制拟合直线求第二个交点的图像
def profitFindSecondPointGraph(filename,v):
    x6,y6=getXt1AndXt2.getFirstProfitPoint(filename,v)
    plt.scatter(x6[:], y6[:], 25, 'yellow')
    x1,y1=getXt1AndXt2.getFirstLinePoint(filename,v)
    plt.plot(x1, y1, 'blue', label='[-5,-3]的拟合直线')
    x7,y7=getXt1AndXt2.getSecondProfitPoint(filename,v)
    plt.scatter(x7[:], y7[:], 25, 'green')
    x2,y2=getXt1AndXt2.getSecondLinePoint(filename,v)
    plt.plot(x2, y2, 'red', label='[-2.2,-1]的拟合直线')
    x,y=getXt1AndXt2.getSecondPoint(filename,v)
    plt.scatter(x, y, 25, 'black', label=(x, y))
    trWithxtGraph(filename)

#9.绘制拟合直线和曲线求第一个交点的图像
def profitFindFirstPointGraph(filename,v):
    x9,y9=getXt1AndXt2.getTenPoint(filename,v)
    plt.scatter(x9[:],y9[:],25,'yellow')
    x1,y1=getXt1AndXt2.getTenPoint(filename,v)
    plt.plot(x1,y1,'blue',label='取后十个点进行拟合的图像')
    x2,y2=getXt1AndXt2.getFirstLinePoint(filename,v)
    plt.plot(x2, y2, 'red',label='[-5,-3]的拟合直线')
    plt.title('求第一个交点的图像')
    plt.legend()
    plt.grid(True)
    plt.show()
if __name__ == '__main__':
    f2 = 'C:/Users/LFK/Desktop/数据/数据/输入数据1-冷却曲线.csv'
    v=30
    coolGraph(f2)