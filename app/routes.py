from app import app
from flask import render_template, request, abort
from flask_restful import Resource, Api
from marshmallow import Schema, fields
import datetime
import dateutil.parser
import sqlite3
import json

api = Api(app)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class SpeedTestResults(Resource):
    def get(self):
        fromdate = datetime.datetime.now() - datetime.timedelta(days=365)
        todate = datetime.datetime.now()
        if 'fromdate' in request.args:
            fromdate = request.args['fromdate']
        if 'todate' in request.args:
            todate = request.args['todate']
        conn = sqlite3.connect('aussiebbmgt.db')
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute("select * from speedtestresults where date > '%s' and date < '%s' order by id" % (fromdate, todate))
        results = cursor.fetchall()
        conn.close()
        return results

class DpuTestResults(Resource):
    def get(self):
        fromdate = datetime.datetime.now() - datetime.timedelta(days=365)
        todate = datetime.datetime.now()
        if 'fromdate' in request.args:
            fromdate = request.args['fromdate']
        if 'todate' in request.args:
            todate = request.args['todate']
        conn = sqlite3.connect('aussiebbmgt.db')
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute("select * from dpuportstatusresults where completed_at > '%s' and completed_at < '%s' order by id" % (fromdate, todate))
        results = cursor.fetchall()
        conn.close()
        return results

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/combined')
def combined():
    return render_template('combined.html')

@app.route('/test')
def test():
    return render_template('test.html')

api.add_resource(SpeedTestResults, '/speedtestresults')
api.add_resource(DpuTestResults, '/dputestresults')
