import traceback

import pymysql
from flask import Flask
from flask import render_template,request
app=Flask(__name__)

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
            return render_template('index.html')
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
        return render_template('pay.html')
    except:
        #抛出错误信息
        traceback.print_exc()
        # 如果发生错误则回滚
        db.rollback()
        return '注册失败'
    # 关闭数据库连接
    db.close()


if __name__ == '__main__':
    app.run(debug=True)