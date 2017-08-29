import time
import os
import sys

from elasticsearch import Elasticsearch
from flask import Flask, request, render_template, jsonify
from flask_assets import Environment, Bundle
from flask_restful import Resource, Api
from werkzeug.datastructures import ImmutableMultiDict
from app import app

esserver = ['192.168.1.222:9200']

es = Elasticsearch(esserver)
api = Api(app)
assets = Environment(app)

def GetUniqueTimeStamp () :
    return int(time.time() * 10000000000)

def CheckTimeReady (indexname, timeframe_minutes):
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
    if len(result['hits']['hits']) == 0:
        return True
    else:
        return False

class TimeCheck(Resource):
    def post(self):
        json = request.json

        tableindex = json['tableindex']
        timeframe = json['timeframe']

        return CheckTimeReady(tableindex, timeframe)

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
            "PointsEarned": points + 6,
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
            "PointsEarned": int(answer.split(":")[1]) + 1,
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

class GetTotalPoints (Resource):
    def get(self):
        rankfiler = es.search(index='rankfiler_index', body={
        "from" : 0, "size" : 100,
        'query': {
            'match_all':{}
        }
        })['hits']['hits']

        timekeeper = (es.search(index='timekeeper_index', body={
        "from" : 0, "size" : 100,
        'query': {
            'match_all':{}
        }
        }))['hits']['hits']

        count = int(0)
        minimum = int(0)
        currenttime = GetUniqueTimeStamp()
        current_id = currenttime

        for eachitem in rankfiler:
            count += eachitem['_source']['PointsEarned']
            try:
                current_id = int(eachitem['_source']['EpochTime'])
            except:
                current_id
            if minimum == 0 or minimum > current_id:
                minimum = current_id

        for eachitem in timekeeper:
            count += int(eachitem['_source']['PointsEarned'])
        
        hours_from_start = int((currenttime - minimum) / 36000000000000)
        total_score = count - int(hours_from_start/2)
        if total_score < 0:
            total_score = 0

        return total_score

def main(args=None):
    api.add_resource(GetQuestions, '/meiva/api/rankfiler/get/questions')
    
    api.add_resource(GetCategories, '/meiva/api/rankfiler/get/categories')
    api.add_resource(RankFilerForm, '/meiva/api/rankfiler/form/new')

    api.add_resource(GetTimeCategories,'/meiva/api/timekeeper/get/categories')
    api.add_resource(TimeKeeperForm, '/meiva/api/timekeeper/form/new')

    api.add_resource(TimeCheck, '/meiva/api/generic/timecheck')
    api.add_resource(GetTotalPoints, '/meiva/api/generic/get/points')

if __name__ == '__main__':
    returncode = 1
    try:
        main()
        app.run(host= '0.0.0.0',debug=True,threaded=True)
        returncode = 0
    except Exception as errormessage:
        print('Error: %s' % errormessage, file=sys.stderr)
    sys.exit(returncode)