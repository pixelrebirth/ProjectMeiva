import time
import os

from elasticsearch import Elasticsearch
from flask import Flask, request, render_template, jsonify
from flask_restful import Resource, Api
from werkzeug.datastructures import ImmutableMultiDict
from app import app

esserver = ['192.168.1.222:9200']

es = Elasticsearch(esserver)
api = Api(app)

def GetUniqueTimeStamp ():
    return int(time.time() * 10000000000)

def GetEntriesByTime (indexname, timeframe_minutes):
    currenttime = GetUniqueTimeStamp()
    previoustime = currenttime - (timeframe_minutes * 60 * 10000000000)
    result = es.search(index=indexname, body={
        "query": {
            "range" : {
                "EpochTime" : {
                    "gte" : previoustime,
                    "lte" : currenttime
                }
            }
        }
    })
    return result

class RankFilerForm(Resource):
    def post(self):
        form_multidict = request.form
        seperator = ':'
        
        points = len(form_multidict.getlist('answerchecked'))
        print(points)
        print(form_multidict.getlist('answerchecked'))
       
        answered = form_multidict.getlist('answerchecked')
        uid = GetUniqueTimeStamp()
        data = {
            "Type": "rankfiler",
            "UserId":form_multidict.getlist('name')[0],
            "PointsEarned": points,
            "Answers": seperator.join(answered),
            "EpochTime": str(uid)
        }
        ack = es.index(index='rankfiler_index', doc_type='post', id=uid ,body=data)
        return ack

class TimeKeeperForm(Resource):
    def post(self):
        form_multidict = request.form
        answer = form_multidict.getlist('TimeSpent')[0]
        uid = GetUniqueTimeStamp()
        data = {
            "Type": "timekeeper",
            "UserId":form_multidict.getlist('name')[0],
            "PointsEarned": answer.split(":")[1],
            "Answer": answer.split(":")[0],
            "Comment": form_multidict.getlist('comment')[0],
            "EpochTime": str(uid)
        }
        ack = es.index(index='timekeeper_index', doc_type='post', id=uid ,body=data)
        return ack

class GetQuestions (Resource):
    def get(self):
        questions = es.search(index='rankfiler_question_index', body={
            "from" : 0, "size" : 100,
            'query': {
                'match_all':{}
            }
        })
        return questions['hits']['hits']

class GetCategories (Resource):
    def get(self):
        
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

class GetTimeCategories (Resource):
    def get(self):
        questions = es.search(index='timekeeper_question_index', body={
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

api.add_resource(RankFilerForm, '/meiva/api/rankfiler/form/new')
api.add_resource(GetCategories, '/meiva/api/rankfiler/get/categories')
api.add_resource(GetQuestions, '/meiva/api/rankfiler/get/questions')

api.add_resource(GetTimeCategories,'/meiva/api/timekeeper/get/categories')
api.add_resource(TimeKeeperForm, '/meiva/api/timekeeper/form/new')

if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug=True,threaded=True)