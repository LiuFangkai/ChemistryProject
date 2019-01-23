# -*- coding: utf-8 -*-

# __author__="ZJL"


from flask import Flask
from flask import Response

import json

app = Flask(__name__)


def Response_headers(content):
    resp = Response(content)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

from app import getXt1AndXt2
@app.route('/')
def trWithXt():
    x, y = getXt1AndXt2.changeTAndXt('../static/file/20180921185434冷却曲线.csv')
    temp1 = []
    for i in range(len(x)):
        temp = {'x': x[i], 'y': y[i]}
        temp1.append(temp)
    datas = {
        'data': temp1,
    }
    content = json.dumps(datas)
    resp = Response_headers(content)
    return resp

if __name__ == '__main__':
    app.run(debug=True)  # threaded=True,
