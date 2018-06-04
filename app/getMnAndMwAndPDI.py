from app import getHmAndTm, getXt1AndXt2
#filename为升温数据的,Tm为所有温度的平均值
def getMn(Xt2,filename,Lu, Mo, pc, deltaHm0, sigmae, Tm0):
    deltaHm2 = getHmAndTm.getHotHm(filename) * getHmAndTm.getHotHm(filename)
    Tm=getHmAndTm.getAverageTm(filename)
    fz=2*sigmae*deltaHm0*Mo  #分子
    fm = deltaHm2 * Xt2 * Lu * pc * (1 - Tm / Tm0)
    Mn=fz/fm
    return Mn

def getMw(Xt1,Xt2,filename,Lu, Mo, pc, deltaHm0, sigmae, Tm0):
    deltaHm2 = getHmAndTm.getHotHm(filename) * getHmAndTm.getHotHm(filename)
    Tm = getHmAndTm.getMaxTm(filename)
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
    xt1=getXt1AndXt2.getXt1(filename2,v)
    xt2=getXt1AndXt2.getXt2(filename2, v)
    Mn=getMn(xt2, filename3, Lu, Mo, pc, deltaHm0, sigmae, Tm0)
    Mw=getMw(xt1,xt2, filename3, Lu, Mo, pc, deltaHm0, sigmae, Tm0)
    PDI=getPDI(Mn,Mw)
    return Mn,Mw,PDI

if __name__ == '__main__':
    f2='C:/Users/LFK/Desktop/数据/数据/输入数据1-冷却曲线.csv'
    f3='C:/Users/LFK/Desktop/数据/数据/输入数据2-升温曲线.csv'
    # f2= 'C:/Users/LFK/Desktop/数据/数据/MPEO 21k 16C cooling.csv'
    # f3 = 'C:/Users/LFK/Desktop/数据/数据/MPEO 21k 16C heating.csv'
    arr=[0.2167, 42, 0.936, 209.2, 31, 459]
    Lu = float(arr[0])
    Mo = float(arr[1])
    pc = float(arr[2])
    deltaHm0 = float(arr[3])
    sigmae = float(arr[4])
    Tm0 = float(arr[5] - 273.15)
    v=20
    all=getAlldata(f2,f3,v,Lu,Mo,pc,deltaHm0,sigmae,Tm0)
    print(all)