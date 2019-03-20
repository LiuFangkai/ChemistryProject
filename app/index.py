import os
from flask import Flask
from flask import request,Response,render_template,url_for,redirect,make_response
from app import getMnAndMwAndPDI
import json
import traceback
import pymysql
import time
from app.pay import AliPay

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

@app.route('/tryCaculate',methods=['POST'])
def caculate0():
    if request.method == 'POST':
        deltaHm = float(request.form.get('Hm'))
        Lu, Mo, pc, deltaHm0, sigmae, Tm0 = getData(JBXData)
        Mn, Mw, PDI = getMnAndMwAndPDI.getAlldata('./static/file/'+request.form.get('file2'), './static/file/'+request.form.get('file3'), Lu, Mo, pc,
                                                  deltaHm0, sigmae, Tm0, deltaHm)
        data0={
            "Mn":Mn,
            "Mw":Mw,
            "PDI":PDI
        }
        global path2
        global path3
        path2='./static/file/'+request.form.get('file2')
        path3='./static/file/'+request.form.get('file3')
        return Response(json.dumps(data0),content_type='application/json')

@app.route('/index')
def index():
    return render_template('index.html')

# 默认路径访问封面
@app.route('/')
def cover():
    return render_template('cover.html')

#点击登录按钮时跳转
@app.route('/login')
def login():
    return render_template('login.html')

#获取登录参数及处理
@app.route('/login1')
def getLoginRequest():
#查询用户名及密码是否匹配及存在
    #连接数据库,此前在数据库中创建数据库TESTDB
    db = pymysql.connect("localhost","root","root","test" )
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # SQL 查询语句
    sql = "select * from user where user="+request.args.get('user')+" and password="+request.args.get('password')+""
    try:
        # 执行sql语句
        cursor.execute(sql)
        results = cursor.fetchall()
        print(len(results))
        if len(results)==1:
            return redirect(url_for('index'))
        else:
            return '用户名或密码不正确'
        # 提交到数据库执行
        db.commit()
    except:
        # 如果发生错误则回滚
        traceback.print_exc()
        db.rollback()
    # 关闭数据库连接
    db.close()

@app.route('/correctpassword')
def correctpassword():
    return render_template('correctPassword.html')

@app.route('/correctPassword')
def correctPassword():
    #连接数据库,此前在数据库中创建数据库test
    db = pymysql.connect("localhost","root","root","test" )
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # SQL 插入语句
    sql = "UPDATE user set password="+request.args.get('password1')+" where user="+request.args.get('user')+""
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
         #修改成功之后跳转到登录页面
        return render_template('login.html')
    except:
        #抛出错误信息
        traceback.print_exc()
        # 如果发生错误则回滚
        db.rollback()
        return '修改失败'
    # 关闭数据库连接
    db.close()


#单击试用按钮时跳转
@app.route('/try')
def trial():
    return render_template('try.html')

#默认路径访问注册页面
@app.route('/regist')
def regist():
    return render_template('regist.html')

#获取注册请求及处理
@app.route('/register')
def getRigistRequest():
#把用户名和密码注册到数据库中
    #连接数据库,此前在数据库中创建数据库test
    db = pymysql.connect("localhost","root","root","test" )
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # SQL 插入语句
    sql = "INSERT INTO user(user, password) VALUES ("+request.args.get('user')+", "+request.args.get('password')+")"
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
         #注册成功之后跳转到登录页面
        return redirect(url_for('pay'))
    except:
        #抛出错误信息
        traceback.print_exc()
        # 如果发生错误则回滚
        db.rollback()
        return '注册失败'
    # 关闭数据库连接
    db.close()

def get_ali_object():
    # 沙箱环境地址：https://openhome.alipay.com/platform/appDaily.htm?tab=info
    app_id = "2016092500596559"  #  APPID （沙箱应用）

    # 支付完成后，支付偷偷向这里地址发送一个post请求，识别公网IP,如果是 192.168.20.13局域网IP ,支付宝找不到，def page2() 接收不到这个请求
    notify_url = "http://127.0.0.1:5000/page2/"

    # 支付完成后，跳转的地址。
    return_url = "http://127.0.0.1:5000/index"

    merchant_private_key_path = "./static/keys/app_private_2048.txt" # 应用私钥
    alipay_public_key_path = "./static/keys/alipay_public_2048.txt"  # 支付宝公钥

    alipay = AliPay(
        appid=app_id,
        app_notify_url=notify_url,
        return_url=return_url,
        app_private_key_path=merchant_private_key_path,
        alipay_public_key_path=alipay_public_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥
        debug=True,  # 默认False,
    )
    return alipay

@app.route('/pay')
def pay():
    return render_template('pay.html')

@app.route('/pay',methods=['POST'])
def page1():
    # 根据当前用户的配置，生成URL，并跳转。
    money =float(request.form.get("money"))
    print(money)
    alipay = get_ali_object()

    # 生成支付的url
    query_params = alipay.direct_pay(
        subject="结晶聚合物分子量分子量计算系统会员充值",  # 商品简单描述
        out_trade_no="x2" + str(datetime.now().strftime("%Y%m%d%H%M%S")),  # 用户购买的商品订单号（每次不一样）
        total_amount=money,  # 交易金额(单位: 元 保留俩位小数)
    )
    pay_url = "https://openapi.alipaydev.com/gateway.do?{0}".format(query_params)  # 支付宝网关地址（沙箱应用）
    return redirect(pay_url)

@app.route('/page2',methods=['POST'])
def page2():
    alipay = get_ali_object()
    if request.method == "POST":
        # 检测是否支付成功
        # 去请求体中获取所有返回的数据：状态/订单号
        from urllib.parse import parse_qs
        # name&age=123....
        body_str = request.body.decode('utf-8')
        post_data = parse_qs(body_str)

        post_dict = {}
        for k, v in post_data.items():
            post_dict[k] = v[0]

        # post_dict有10key： 9 ，1
        sign = post_dict.pop('sign', None)
        status = alipay.verify(post_dict, sign)
        print('------------------开始------------------')
        print('POST验证', status)
        print(post_dict)
        out_trade_no = post_dict['out_trade_no']

        # 修改订单状态
        # models.Order.objects.filter(trade_no=out_trade_no).update(status=2)
        print('------------------结束------------------')
        # 修改订单状态：获取订单号
        return make_response('index')

    else:
        params = request.GET.dict()
        sign = params.pop('sign', None)
        status = alipay.verify(params, sign)
        print('==================开始==================')
        print('GET验证', status)
        print('==================结束==================')
        return redirect('index')



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