from flask import render_template
from app import app
import requests

@app.route('/')
@app.route('/index')
def index():
    questions = requests.get('http://127.0.0.1:5000/meiva/api/rankfiler/get/questions')
    categories = requests.get('http://127.0.0.1:5000/meiva/api/rankfiler/get/categories')
    time_categories = requests.get('http://127.0.0.1:5000/meiva/api/timekeeper/get/categories')

    timejson = {'tableindex': 'timekeeper_index','timeframe': 45}
    timekeeper_ready = requests.post('http://127.0.0.1:5000/meiva/api/generic/timecheck',json=timejson)

    rankjson = {'tableindex': 'rankfiler_index','timeframe': 1410}
    rankfiler_ready = requests.post('http://127.0.0.1:5000/meiva/api/generic/timecheck',json=rankjson)

    total_points = requests.get('http://127.0.0.1:5000/meiva/api/generic/get/points')

    return render_template('index.html',
                           title='Project Meiva',
                           questions = questions.json(),
                           categories = categories.json(),
                           time_categories = time_categories.json(),
                           rankfiler_ready = rankfiler_ready.json(),
                           timekeeper_ready = timekeeper_ready.json(),
                           total_points = total_points.json()
    )


@app.route('/indexChart')
def indexChart(chartID = 'chart_ID', chart_type = 'area', chart_height = 350):
	chart = {"renderTo": chartID, "pie": chart_type, "height": chart_height}
	series = [{"name": 'Label1', "data": [1,7,3]}, {"name": 'Label2', "data": [4, 2, 6]}, {"name": 'Label3', "data": [1, 4, 10]}]
	title = {"text": 'My Title'}
	xAxis = {"categories": ['xAxis Data1', 'xAxis Data2', 'xAxis Data3']}
	yAxis = {"title": {"text": 'yAxis Label'}}
	return render_template('indexChart.html', 
                            chartID=chartID,
                            chart=chart,
                            series=series,
                            title=title,
                            xAxis=xAxis,
                            yAxis=yAxis
    )