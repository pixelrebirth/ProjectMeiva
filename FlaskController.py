import time
import os

from elasticsearch import Elasticsearch
from flask import Flask, request
from flask_restful import Resource, Api

esserver = ['192.168.1.222:9200']

es = Elasticsearch(esserver)
app = Flask(__name__, static_url_path='')
api = Api(app)

def GetUniqueTimeStamp ():
    return int(time.time() * 10000000000)

def GetPointsByCategory(category):
    case = {
        "Coding": 1,
        "Sports Talk": 0,
        "Discussion": 1,
        "Complaining": 0,
        "Pacing": 0,
        "Chores": 1
    }
    try:
        if case[category] in (0,1):
            return case[category]
        else:
            return 0
    except:
        return 0

class TimeKeeperNew(Resource):
    def post(self):
        json = request.json
        print(json)
        
        category =json['TimeCategory']
        data = {
            "UserId":json['userid'],
            "TimeCategory": category,
            "PointsEarned": GetPointsByCategory(category),
            "Type": "timekeeper"
        }
        uid = GetUniqueTimeStamp()
        ack = es.index(index='meiva_index', doc_type='post', id=uid ,body=data)

        return ack

class RankFilerNew(Resource):
    def post(self):
        json = request.json
        print(json)

        checked =json['answerchecked']
        if checked == "1":
            points = 1
        else:
            points = 0
        
        data = {
            "Type": "rankfiler",
            "UserId":json['userid'],
            "PointsEarned": points,
            "RankType":json['ranktype'],
            "Answers": checked
        }
        uid = GetUniqueTimeStamp()
        ack = es.index(index='meiva_index', doc_type='post', id=uid ,body=data)
        return ack

        
@app.route('/')
def root():
    return app.send_static_file('index.html')

api.add_resource(TimeKeeperNew, '/meiva/api/timekeeper/new')
api.add_resource(RankFilerNew, '/meiva/api/rankfiler/new')

if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug=True)