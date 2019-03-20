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
@app.route('/')
def drawCorrect():
    x0,y0=getXt1AndXt2.readCsv('../static/file/20180921185434冷却曲线.csv')
    x,y = getXt1AndXt2.correct('../static/file/20180921185434冷却曲线.csv')
    xx = [x[0], x[-1]]
    yy = [y[0], y[-1]]
    print(yy)
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
    print(temp2)
    datas={
        'data1':temp1,
        'data2':temp2
    }
    content = json.dumps(datas)
    resp = Response_headers(content)
    return resp

if __name__ == '__main__':
    app.run(debug=True)  # threaded=True,
