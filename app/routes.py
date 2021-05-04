import datetime
import sqlite3
from urllib.parse import unquote
from flask import render_template, request
from flask_restful import Resource, Api
from app import app

api = Api(app)

def dict_factory(cursor, row):
    data = {}
    for idx, col in enumerate(cursor.description):
        data[col[0]] = row[idx]
    return data

class SpeedTestResults(Resource):
    def get(self):
        fromdate_raw = datetime.datetime.now() - datetime.timedelta(days=365)
        fromdate = fromdate_raw.isoformat()
        todate = datetime.datetime.now().isoformat()
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
        fromdate_raw = datetime.datetime.now() - datetime.timedelta(days=365)
        fromdate = fromdate_raw.isoformat()
        todate = datetime.datetime.now().isoformat()
        if 'fromdate' in request.args:
            fromdate = request.args['fromdate']
        if 'todate' in request.args:
            todate = request.args['todate']
        conn = sqlite3.connect('aussiebbmgt.db')
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute("select * from dpuportstatusresults where syncState != 'None' and operationalState != 'None' and completed_at > '%s' and completed_at < '%s' order by id" % (fromdate, todate))
        results = cursor.fetchall()
        conn.close()
        return results

class Settings(Resource):
    def get(self):
        query = "select * from settings"
        if 'key' in request.args:
            query = "select * from settings where key = '%s'" % (request.args['key'])
        conn = sqlite3.connect('aussiebbmgt.db')
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return results

    def post(self):
        conn = sqlite3.connect('aussiebbmgt.db')
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        for key in request.form.keys():
            value = unquote(request.form.get(key))
            cursor.execute("insert into settings(key,value) values ('%s', '%s') on conflict(key) do update set value='%s' where key='%s'" % (key, value, value, key))
            conn.commit()
        results = cursor.fetchall()
        conn.close()
        return results

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return ''

api.add_resource(SpeedTestResults, '/speedtestresults')
api.add_resource(DpuTestResults, '/dputestresults')
api.add_resource(Settings, '/settings')
