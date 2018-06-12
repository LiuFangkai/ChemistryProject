from app import getHmAndTm, getXt1AndXt2
#步骤1，计算Mn，其中deltaHm为熔融焓（不同分子量，deltaHm不同），Tm为平均温度（计算Mw和Mn使用温度不同）
#filename3为升温数据的,deltaHm为熔融焓，用户自己输入
def getMn(Xt2,filename3,Lu, Mo, pc, deltaHm0, sigmae, Tm0,deltaHm):
    deltaHm2=deltaHm*deltaHm
    Tm=getHmAndTm.getAverageTm(filename3)
    fz=2*sigmae*deltaHm0*Mo  #分子
    fm = deltaHm2 * Xt2 * Lu * pc * (1 - Tm / Tm0)
    Mn=fz/fm
    return Mn

#步骤2，计算Mw，Tm为平均温度
def getMw(Xt1,Xt2,filename3,Lu, Mo, pc, deltaHm0, sigmae, Tm0,deltaHm):
    Tm = getHmAndTm.getTmOfMw(filename3)
    deltaHm2 =deltaHm*deltaHm
    fz = 2 * sigmae * deltaHm0 * Mo  # 分子
    fm = deltaHm2 * Xt1 * Lu * pc * (1 - Tm / Tm0)
    fm1= deltaHm2 * Xt2 * Lu * pc * (1 - Tm / Tm0)
    Mi1=fz/fm
    Mi2=fz/fm1
    Mw=(Mi1+Mi2)/2
    return Mw

def getPDI(Mn,Mw):
    PDI=Mw/Mn
    return PDI

#步骤3，计算Mn，Mw和PDI
def getAlldata(filename2,filename3,Lu, Mo, pc, deltaHm0, sigmae, Tm0,deltaHm):
    xt1=getXt1AndXt2.getXt1(filename2)
    xt2=getXt1AndXt2.getXt2(filename2)
    Mn=getMn(xt2,filename3, Lu, Mo, pc, deltaHm0, sigmae, Tm0,deltaHm)
    Mw=getMw(xt1,xt2, filename3, Lu, Mo, pc, deltaHm0, sigmae, Tm0,deltaHm)
    PDI=getPDI(Mn,Mw)
    return Mn,Mw,PDI

if __name__ == '__main__':
    # f2='C:/Users/LFK/Desktop/数据/数据/输入数据1-冷却曲线.csv'
    # f3='C:/Users/LFK/Desktop/数据/数据/输入数据2-升温曲线.csv'
    arr = [0.2167, 42, 0.936, 209.2, 30, 459 - 273.15]

    f2= 'C:/Users/LFK/Desktop/数据/数据/MPEO 21k 16C cooling.csv'
    f3 = 'C:/Users/LFK/Desktop/数据/数据/MPEO 21k 16C heating.csv'
    # f2 = 'C:/Users/LFK/Documents/WeChat Files/LFK613/Files/PP F401 10K-min cooling.csv'
    # f3 = 'C:/Users/LFK/Documents/WeChat Files/LFK613/Files/PP F401 heating after 10K-min.csv'
    # arr = [0.2783, 44, 1.228, 220, 31, 69]
    Lu = float(arr[0])
    Mo = float(arr[1])
    pc = float(arr[2])
    deltaHm0 = float(arr[3])
    sigmae = float(arr[4])
    Tm0 = float(arr[5])
    deltaHm=175
    all=getAlldata(f2,f3,Lu,Mo,pc,deltaHm0,sigmae,Tm0,deltaHm)
    print("Mn:%f,Mw:%f,PDI:%f"%(all[0],all[1],all[2]))