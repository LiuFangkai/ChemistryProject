import csv
import re
from hot import getHmAndTm
from cool import getXt1AndXt2

def func(s):
    num=re.sub('[nmJ/gJ/molK]','',s)
    return float(num)
#该文件中的filename为高分子类型，对应于前端的标签file1
def readCategoryCSV(filename):
    with open(filename) as f:
        read = csv.reader(f)
        for i, rows in enumerate(read):
            if i == 1:
                row = rows
    return row

def getMn(Xt2,filename1,filename3):
    row=readCategoryCSV(filename1)
    Lu = func(row[1])
    Mo = func(row[2])
    pc = func(row[3])
    deltaHm0= func(row[5])
    deltaHm2= getHmAndTm.getHotHm(filename3) * getHmAndTm.getHotHm(filename3)
    sigmae = func(row[6])
    Tm0= func(row[7])-273.15
    # print(Lu,Mo,pc,deltaHm0,deltaHm2,sigmae,Tm0)
    fz=2*sigmae*deltaHm0*Mo  #分子
    maxTm=getHmAndTm.getXofmaxy(filename3)
    fm = deltaHm2 * Xt2 * Lu * pc * (1 - maxTm / Tm0)
    Mn=fz/fm
    return Mn

def getMw(Xt1,filename,filename3):
    Mw=getMn(Xt1,filename,filename3)
    return Mw

def getPDI(Mn,Mw):
    PDI=Mw/Mn
    return PDI

#和前端对应,file1为高分子类型，file2为降温曲线，file3为升温曲线
def getAlldata(filename1,filename2,filename3,v):
    Mn=getMn(getXt1AndXt2.getXt2(filename2,v),filename1,filename3)
    Mw=getMw(getXt1AndXt2.getXt1(filename2,v),filename1,filename3)
    PDI=getPDI(Mn,Mw)
    return Mn,Mw,PDI

if __name__ == '__main__':
    f1='C:/Users/LFK/Desktop/数据/数据/输入数据4-高分子类型与参数.csv'
    f2='C:/Users/LFK/Desktop/数据/数据/输入数据1-冷却曲线.csv'
    f3='C:/Users/LFK/Desktop/数据/数据/输入数据2-升温曲线.csv'
    v=20
    all=getAlldata(f1,f2,f3,v)
    print(all)