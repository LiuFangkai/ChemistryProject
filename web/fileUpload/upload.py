
import os

from flask import send_from_directory, render_template
from flask import Flask, request
from caculatMnAndMw import getMnAndMwPDI
ALLOWED_EXTENSIONS = set(['txt','csv'])
#python3自动生成文件名
from datetime import *


tmp = 'static/file'
curdir = os.path.abspath('.')  # 获得当前工作目录,如果在加一个点，是获得当前目录的父目录
UPLOAD_FOLDER = curdir + os.path.altsep + tmp + os.path.altsep  # 该路径为当前文件夹拼接windows下文件分隔符再拼接‘tmp'文件夹，再拼接文件分隔符
if os.path.exists(UPLOAD_FOLDER)==False:
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
    uploadpath1=upload_single_file('file1')
    uploadpath2 = upload_single_file('file2')
    uploadpath3 = upload_single_file('file3')
    return uploadpath1,uploadpath2,uploadpath3

#从前台form中获得v的值
def getv():
    velocity=int(request.form.get('velocity'))
    return velocity

#计算所得到的值，并返回
def caculate():
    path1,path2,path3=upload_all_file()
    v=getv()
    Mn,Mw,PDI=getMnAndMwPDI.getAlldata(path1,path2,path3,v)
    return Mn,Mw,PDI

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        Mn,Mw,PDI=caculate()
        data={
            'Mn':Mn,
            'Mw':Mw,
            'PDI':PDI
        }
        return render_template('result.html',data=data)
    return render_template('upload.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

if __name__ == '__main__':
    app.run(debug=True)