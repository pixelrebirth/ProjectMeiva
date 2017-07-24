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

        points = 0
        answered = []
        checked = json['answerchecked']
        keys_in_json = list(checked.keys())
        for key in keys_in_json:
            points += int(checked[key])
            if points == 1:
                answered += key

        seperator = ':'
        data = {
            "Type": "rankfiler",
            "UserId":json['userid'],
            "PointsEarned": points,
            "RankType":json['ranktype'],
            "Answers": seperator.join(answered)
        }
        uid = GetUniqueTimeStamp()
        ack = es.index(index='meiva_index', doc_type='post', id=uid ,body=data)
        return ack
class GetQuestions (Resource):
    def post(self):
        json = request.json
        category = json['category']
        print(json)

        question = es.search(index='rankfiler_question_index', body={
            "from" : 0, "size" : 100,
            'query': {
                "query_string" : {
                    "default_field" : "category",
                    "query" : category.replace(" "," AND ")
                }
            }
        })
        return question['hits']['hits']
class GetCategories (Resource):
    def post(self):
        
        questions = es.search(index='rankfiler_question_index', body={
        "from" : 0, "size" : 100,
        'query': {
            'match_all':{}
        }
        })

        allcategories = []
        for category in questions['hits']['hits']:
            allcategories += {(category['_source']['category'])}
        listSet = list(set(allcategories))
        listSet.sort()
        return listSet

        
@app.route('/')
def root():
    return app.send_static_file('index.html')

api.add_resource(TimeKeeperNew, '/meiva/api/timekeeper/new')
api.add_resource(RankFilerNew, '/meiva/api/rankfiler/new')
api.add_resource(GetCategories, '/meiva/api/rankfiler/get/categories')
api.add_resource(GetQuestions, '/meiva/api/rankfiler/get/questions')

if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug=True)