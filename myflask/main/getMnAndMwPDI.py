from myflask.main import getHmAndTm, getXt1AndXt2


def getMn(Xt2,filename3,Lu, Mo, pc, deltaHm0, sigmae, Tm0):
    deltaHm2 = getHmAndTm.getHotHm(filename3) * getHmAndTm.getHotHm(filename3)
    fz=2*sigmae*deltaHm0*Mo  #分子
    maxTm= getHmAndTm.getXofmaxy(filename3)
    fm = deltaHm2 * Xt2 * Lu * pc * (1 - maxTm / Tm0)
    Mn=fz/fm
    return Mn

def getMw(Xt1,filename3,Lu, Mo, pc, deltaHm0, sigmae, Tm0):
    Mw=getMn(Xt1,filename3,Lu, Mo, pc, deltaHm0, sigmae, Tm0)
    return Mw

def getPDI(Mn,Mw):
    PDI=Mw/Mn
    return PDI

#和前端对应,file1为高分子类型，file2为降温曲线，file3为升温曲线
def getAlldata(filename2,filename3,v,Lu, Mo, pc, deltaHm0, sigmae, Tm0):
    Mn=getMn(getXt1AndXt2.getXt2(filename2, v), filename3, Lu, Mo, pc, deltaHm0, sigmae, Tm0)
    Mw1=getMw(getXt1AndXt2.getXt1(filename2, v), filename3, Lu, Mo, pc, deltaHm0, sigmae, Tm0)
    Mw=(Mn+Mw1)/2
    PDI=getPDI(Mn,Mw)
    return Mn,Mw,PDI

if __name__ == '__main__':
    f2='C:/Users/LFK/Desktop/数据/数据/输入数据1-冷却曲线.csv'
    f3='C:/Users/LFK/Desktop/数据/数据/输入数据2-升温曲线.csv'
    arr=[2.167, 42, 0.936, 209.2, 31, 459]
    Lu = float(arr[0])
    Mo = float(arr[1])
    pc = float(arr[2])
    deltaHm0 = float(arr[3])
    sigmae = float(arr[4])
    Tm0 = float(arr[5] - 273.15)
    v=20
    all=getAlldata(f2,f3,v,Lu,Mo,pc,deltaHm0,sigmae,Tm0)
    print(all)