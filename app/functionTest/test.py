from flask import render_template
from flask import Flask, request
import json
app = Flask(__name__)

@app.route('/',methods=['GET','POST'])
def add():
    data={'a':1,
          'b':2}
    content=json.dumps(data)
    return content

if __name__ == '__main__':
    app.run(debug=True)