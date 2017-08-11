from flask import Flask, request, render_template
from app import app
import requests

@app.route('/')
@app.route('/index')
def index():
    questions = requests.get('http://127.0.0.1:5000/meiva/api/rankfiler/get/questions')
    categories = requests.get('http://127.0.0.1:5000/meiva/api/rankfiler/get/categories')
    time_categories = requests.get('http://127.0.0.1:5000/meiva/api/timekeeper/get/categories')

    timejson = {'tableindex': 'timekeeper_index','timeframe': 55}
    timekeeper_ready = requests.post('http://127.0.0.1:5000/meiva/api/generic/timecheck',json=timejson)

    rankjson = {'tableindex': 'rankfiler_index','timeframe': 1435}
    rankfiler_ready = requests.post('http://127.0.0.1:5000/meiva/api/generic/timecheck',json=rankjson)

    return render_template('index.html',
                           title='Project Meiva',
                           questions = questions.json(),
                           categories = categories.json(),
                           time_categories = time_categories.json(),
                           rankfiler_ready = rankfiler_ready.json(),
                           timekeeper_ready = timekeeper_ready.json()
    )
