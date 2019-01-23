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
def drawCorrect():
    fx1,fy1= getXt1AndXt2.getFirstProfitPoint('../static/file/20180921185434冷却曲线.csv')
    x1, y1 = getXt1AndXt2.getFirstLinePoint('../static/file/20180921185434冷却曲线.csv')
    fx2,fy2= getXt1AndXt2.getSecondProfitPoint('../static/file/20180921185434冷却曲线.csv')
    x2, y2 = getXt1AndXt2.getSecondLinePoint('../static/file/20180921185434冷却曲线.csv')

    fx, fy = getXt1AndXt2.getPointOfIntersection('../static/file/20180921185434冷却曲线.csv')

    x, y = getXt1AndXt2.changeTAndXt('../static/file/20180921185434冷却曲线.csv')
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
    content = json.dumps(datas)
    resp = Response_headers(content)
    return resp

if __name__ == '__main__':
    app.run(debug=True)  # threaded=True,
