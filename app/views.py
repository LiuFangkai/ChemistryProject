import json
import time
from app.pay import AliPay
from flask import Flask
from flask import render_template,request,redirect
app = Flask(__name__)

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

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/')
def pay():
    return render_template('pay.html')

@app.route('/',methods=['POST'])
def page1():
    # 根据当前用户的配置，生成URL，并跳转。
    money =float(request.form.get("money"))
    print(money)
    alipay = get_ali_object()

    # 生成支付的url
    query_params = alipay.direct_pay(
        subject="结晶聚合物分子量分子量计算系统会员充值",  # 商品简单描述
        out_trade_no="x2" + str(time.time()),  # 用户购买的商品订单号（每次不一样）
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

if __name__ == '__main__':
    app.run(debug=True)
