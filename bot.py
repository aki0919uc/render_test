from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    CarNum = input('input CarNumber:')
    return CarNum
