from flask import Flask, request, render_template
from app import app
import requests

@app.route('/')
@app.route('/index')
def index():
    questions = requests.get('http://127.0.0.1:5000/meiva/api/rankfiler/get/questions')
    categories = requests.get('http://127.0.0.1:5000/meiva/api/rankfiler/get/categories')
    time_categories = requests.get('http://127.0.0.1:5000/meiva/api/timekeeper/get/categories')

    timejson = {'tableindex': 'timekeeper_index','timeframe': 60}
    timekeeper_notready = requests.post('http://127.0.0.1:5000/meiva/api/generic/timecheck',timejson)
    print(timekeeper_notready)
    
    rankjson = {'tableindex': 'timekeeper_index','timeframe': 1440}
    rankfiler_notready = requests.post('http://127.0.0.1:5000/meiva/api/generic/timecheck',rankjson)
    print(rankfiler_notready)

    return render_template('index.html',
                           title='Project Meiva',
                           questions = questions.json(),
                           categories = categories.json(),
                           time_categories = time_categories.json()
    )
