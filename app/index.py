import os
from flask import render_template
from flask import Flask, request
from app import getMnAndMwAndPDI
from flask import redirect,url_for
import json
from flask import Response

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
path2=""
path3=""
Lu=0
Mo=0
pc=0
deltaHm0=0
sigmae=0
Tm0=0
deltaHm=0
def caculate(**kwargs):
    global path2
    global path3
    global Lu, Mo, pc, deltaHm0, sigmae, Tm0,deltaHm
    path2,path3=upload_all_file()
    # v=int(request.form.get('velocity'))  #获取前台的v值
    deltaHm=float(request.form.get('Hm'))
    if request.form.get("select") == 'JuBingXi':  #获取前台select中选中的value值
        Lu, Mo, pc, deltaHm0, sigmae, Tm0 = getData(JBXData)
    if request.form.get("select") == 'JuYangHuaYiXi':
        Lu, Mo, pc, deltaHm0, sigmae, Tm0 = getData(JBXData)
    Mn,Mw,PDI=getMnAndMwAndPDI.getAlldata(path2, path3, Lu, Mo, pc, deltaHm0, sigmae, Tm0,deltaHm,**kwargs)
    return Mn,Mw,PDI

@app.route('/')
def index():
    return render_template('index.html')

data0={}
@app.route('/upload',methods=['POST'])
def upload(**kwargs):
    global data0
    if request.method == 'POST':
        Mn,Mw,PDI=caculate(**kwargs)
        data0={
            "Mn":Mn,
            "Mw":Mw,
            "PDI":PDI
        }
        return Response(json.dumps(data0),content_type='application/json')

#画原始图
@app.route('/drawCool',methods=['get'])
def draw_cool():
    x, y = getXt1AndXt2.readCsv(path2)
    temp1= []
    for i in range(len(x)):
        temp = {'x': x[i], 'y': y[i]}
        temp1.append(temp)
    datas = {
        "data": temp1
    }
    return Response(json.dumps(datas), content_type='application/json')


@app.route('/drawHeat',methods=['get'])
def draw_heat():
    x, y = getXt1AndXt2.readCsv(path3)
    temp1= []
    for i in range(len(x)):
        temp = {'x': x[i], 'y': y[i]}
        temp1.append(temp)
    datas = {
        "data": temp1
    }
    return Response(json.dumps(datas), content_type='application/json')

#画基线修正后的图
from app import getXt1AndXt2
@app.route('/drawCorrectCool')
def drawCorrectCool():
    x1, y1 = getXt1AndXt2.correct(path2,**kwargs)  #这个显示的是纠正后的数据
    xx = [x1[0], x1[len(x1) - 1]]
    yy = [y1[0], y1[len(x1) - 1]]

    # x, y = getXt1AndXt2.readCsv(path2)
    temp1=[]
    for i in range(len(x1)):
        temp={'x':x1[i],'y':y1[i]}
        temp1.append(temp)
    temp2={
        'start':{
            'x':xx[0],
            'y':yy[0]
        },
        'end':{
            'x':xx[1],
            'y':yy[1]
        }
    }
    datas={
        'data1':temp1,
        'data2':temp2
    }
    return Response(json.dumps(datas), content_type='application/json')

@app.route('/drawCorrectOriginCool')
def drawCorrectOriginCool():
    x1, y1 = getXt1AndXt2.correct(path2,**kwargs)  #这个显示的是纠正后的数据
    xx = [x1[0], x1[len(x1) - 1]]
    yy = [y1[0], y1[len(x1) - 1]]

    x0,y0= getXt1AndXt2.readCsv(path2)
    temp1=[]
    for i in range(len(x0)):
        temp={'x':x0[i],'y':y0[i]}
        temp1.append(temp)
    temp2={
        'start':{
            'x':xx[0],
            'y':yy[0]
        },
        'end':{
            'x':xx[1],
            'y':yy[1]
        }
    }
    datas={
        'data1':temp1,
        'data2':temp2
    }
    return Response(json.dumps(datas), content_type='application/json')


from app import getHmAndTm
@app.route('/drawCorrectHeat')
def drawCorrectHeat():
    x1, y1 = getHmAndTm.correctHot(path3,**kwargs)  # 这个显示的是纠正后的数据
    xx = [x1[0], x1[len(x1) - 1]]
    yy = [y1[0], y1[len(x1) - 1]]

    # x,y=getXt1AndXt2.readCsv(path3)
    temp1=[]
    for i in range(len(x1)):
        temp={'x':x1[i],'y':y1[i]}
        temp1.append(temp)
    temp2={
        'start':{
            'x':xx[0],
            'y':yy[0]
        },
        'end':{
            'x':xx[1],
            'y':yy[1]
        }
    }
    datas={
        'data1':temp1,
        'data2':temp2
    }
    return Response(json.dumps(datas), content_type='application/json')

@app.route('/drawCorrectOriginHeat')
def drawCorrectOriginHeat():
    x1, y1 = getHmAndTm.correctHot(path3,**kwargs)  # 这个显示的是纠正后的数据
    xx = [x1[0], x1[len(x1) - 1]]
    yy = [y1[0], y1[len(x1) - 1]]

    x0,y0=getXt1AndXt2.readCsv(path3)
    temp1=[]
    for i in range(len(x0)):
        temp={'x':x0[i],'y':y0[i]}
        temp1.append(temp)
    temp2={
        'start':{
            'x':xx[0],
            'y':yy[0]
        },
        'end':{
            'x':xx[1],
            'y':yy[1]
        }
    }
    datas={
        'data1':temp1,
        'data2':temp2
    }
    return Response(json.dumps(datas), content_type='application/json')

#画相对结晶度随时间、温度变化的图
@app.route('/xtWithTime')
def xtWithTGraph():
    x= getXt1AndXt2.temperatureToTime(path2,**kwargs)
    y= getXt1AndXt2.caculateXt(path2,**kwargs)
    temp1=[]
    for i in range(len(x)):
        temp={'x':x[i],'y':y[i]}
        temp1.append(temp)
    datas = {
        'data': temp1,
    }
    return Response(json.dumps(datas), content_type='application/json')

@app.route('/xtWithTemperature')
def xtWithTemperature():
    x = getXt1AndXt2.correct(path2,**kwargs)[0]
    y = getXt1AndXt2.caculateXt(path2,**kwargs)
    temp1 = []
    for i in range(len(x)):
        temp = {'x': x[i], 'y': y[i]}
        temp1.append(temp)
    datas = {
        'data': temp1,
    }
    return Response(json.dumps(datas), content_type='application/json')

@app.route('/trWithXt')
def trWithXt():
    x, y = getXt1AndXt2.changeTAndXt(path2,**kwargs)
    temp1 = []
    for i in range(len(x)):
        temp = {'x': x[i], 'y': y[i]}
        temp1.append(temp)
    datas = {
        'data': temp1,
    }
    return Response(json.dumps(datas), content_type='application/json')

@app.route('/intersection')
def intersection():
    fx1,fy1= getXt1AndXt2.getFirstProfitPoint(path2,**kwargs)
    x1, y1 = getXt1AndXt2.getFirstLinePoint(path2,**kwargs)
    fx2,fy2= getXt1AndXt2.getSecondProfitPoint(path2,**kwargs)
    x2, y2 = getXt1AndXt2.getSecondLinePoint(path2,**kwargs)
    fx, fy = getXt1AndXt2.getPointOfIntersection(path2,**kwargs)
    x, y = getXt1AndXt2.changeTAndXt(path2,**kwargs)

    tempf1=[]
    temp1=[]
    tempf2=[]
    temp2=[]
    temp=[]
    for i in range(len(fx1)):
        tempf1.append({'x':fx1[i],'y':fy1[i]})
    for i in range(len(x1)):
        temp1.append({'x':x1[i],'y':y1[i]})
    for i in range(len(fx2)):
        tempf2.append({'x':fx2[i],'y':fy2[i]})
    for i in range(len(x2)):
        temp2.append({'x':x2[i],'y':y2[i]})
    for i in range(len(x)):
        temp.append({'x':x[i],'y':y[i]})
    datas={
        'Intersection':{
            'x':fx,
            'y':fy
        },
        'firstProfitPoint':tempf1,
        'firstLine':temp1,
        'secondProfitPoint':tempf2,
        'secondLine':temp2,
        'originLine':temp
    }
    return Response(json.dumps(datas), content_type='application/json')

@app.route('/correct')
def correct(**kwargs):
    cool=getXt1AndXt2.correct(path2,**kwargs)[0]
    coolStart=cool[0]
    coolEnd=cool[-1]

    heat=getHmAndTm.correctHot(path3,**kwargs)[0]
    heatStart=heat[0]
    heatEnd=heat[-1]

    leftStart=getXt1AndXt2.leftStart
    leftEnd=getXt1AndXt2.leftEnd

    rightStart=getXt1AndXt2.rightStart
    rightEnd=getXt1AndXt2.rightEnd

    data={
        'coolStart':coolStart,'coolEnd':coolEnd,
        'heatStart':heatStart,'heatEnd':heatEnd,
        'leftStart':leftStart,'leftEnd':leftEnd,
        'rightStart':rightStart,'rightEnd':rightEnd
    }

    return render_template('correct.html',data=data)

kwargs={}
@app.route('/modify',methods=['GET'])
def modify():
    coolStart=float(request.args.get("coolStart"))
    coolEnd=float(request.args.get("coolEnd"))
    heatStart=float(request.args.get("heatStart"))
    heatEnd=float(request.args.get("heatEnd"))
    leftStart=float(request.args.get("leftStart"))
    rightStart=float(request.args.get("rightStart"))
    leftEnd=float(request.args.get("leftEnd"))
    rightEnd=float(request.args.get("rightEnd"))
    global kwargs
    kwargs={
        'coolStart':coolStart,'coolEnd':coolEnd,
        'heatStart':heatStart,'heatEnd':heatEnd,
        'leftStart':leftStart,'leftEnd':leftEnd,
        'rightStart':rightStart,'rightEnd':rightEnd
    }
    dels=[]
    for key in kwargs.keys():
        if(kwargs[key]==0):
            dels.append(key)
        else:
            pass
    for key in dels:
        del kwargs[key]

    Mn0,Mw0,PDI0=getMnAndMwAndPDI.getAlldata(path2, path3, Lu, Mo, pc, deltaHm0, sigmae, Tm0,deltaHm)
    data0 = {
        "Mn": Mn0,
        "Mw": Mw0,
        "PDI": PDI0
    }

    Mn1,Mw1,PDI1=getMnAndMwAndPDI.getAlldata(path2, path3, Lu, Mo, pc, deltaHm0, sigmae, Tm0,deltaHm,**kwargs)
    data1 = {
        "Mn": Mn1,
        "Mw": Mw1,
        "PDI": PDI1
    }
    datas={
        'data0':data0,
        'data1':data1
    }
    return Response(json.dumps(datas), content_type='application/json')


if __name__ == '__main__':
    app.run(debug=True)