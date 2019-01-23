# -*- coding: utf-8 -*-

# __author__="ZJL"


from flask import Flask

from flask import request

from flask import Response

import json

app = Flask(__name__)


def Response_headers(content):
    resp = Response(content)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

from app import getXt1AndXt2
@app.route('/cool')
def echarts():
    x,y = getXt1AndXt2.readCsv('../static/file/20180921185434冷却曲线.csv')
    temp1=[]
    for i in range(len(x)):
        temp={'x':x[i],'y':y[i]}
        temp1.append(temp)
    # with open('../static/file/20180921185434冷却曲线.csv', encoding="UTF-8") as f:
    #     datas = f.readlines()
    #     temps = []
    #     for data in datas:
    #         x, y = data.split(',')
    #         temp={'x':x,'y':y}
    #         temps.append(temp)
    #     datas = {
    #         "data": temps
    #     }
    #     print(temps)
    datas = {
        "data": temp1
    }
    content = json.dumps(datas)
    resp = Response_headers(content)
    return resp

if __name__ == '__main__':
    app.run(debug=True)  # threaded=True,
