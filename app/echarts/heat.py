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

# @app.route('/')
# def hello_world():
#     return Response_headers('hello world')

# @app.route('/echarts')
# def echarts():
#     with open('../static/file/20180921185434升温曲线.csv', encoding="UTF-8") as f:
#         datas = f.readlines()
#         temps = []
#         for data in datas:
#             x, y = data.split(',')
#             temp={'x':x,'y':y}
#             temps.append(temp)
#         datas = {
#             "data": temps
#         }
#         print(temps)
#     content = json.dumps(datas)
#     resp = Response_headers(content)
#     return resp

from app import getHmAndTm
@app.route('/')
def drawCorrect():
    x, y = getHmAndTm.correctHot('../static/file/20180921185434升温曲线.csv',heatStart=84.1086)
    xx = [x[0], x[len(x) - 1]]
    yy = [y[0], y[len(x) - 1]]
    temp1=[]
    for i in range(len(x)):
        temp={'x':x[i],'y':y[i]}
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
    content = json.dumps(datas)
    resp = Response_headers(content)
    return resp

if __name__ == '__main__':
    app.run(debug=True)  # threaded=True,
