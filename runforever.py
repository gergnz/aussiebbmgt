#!/usr/bin/env python
"""
This will run forever and check the time to see if it should run again.
When it runs it runs a speed test and dpu port status test.
We then fetch the results and save them locally.
"""

import time
import datetime
import os
import random
import sqlite3
import aussiebb.portal as portal

def runsql(query):
    """run the supplied query"""
    conn = sqlite3.connect('aussiebbmgt.db')
    cursor = conn.cursor()
    results = cursor.execute(query)
    conn.commit()
    response = results.fetchall()
    conn.close()
    return response

def getsettings():
    """get all the settings"""

    _settings={}
    # read in the cadence
    try:
        _settings['cadence'] = runsql("select value from settings where key='cadence'")[0][0]
    except: #pylint: disable=bare-except
        runsql("insert into settings(key,value) values ('cadence', 24)")
        _settings['cadence'] = runsql("select value from settings where key='cadence'")[0][0]

    # read in the random minute and/or set it
    try:
        _settings['minute'] = runsql("select value from settings where key='minute'")[0][0]
    except: #pylint: disable=bare-except
        value = random.randrange(0, 59)
        key = 'minute'
        # pylint: disable=line-too-long
        runsql("insert into settings(key,value) values ('%s', '%s') on conflict(key) do update set value='%s' where key='%s'" % (key, value, value, key))
        # pylint: enable=line-too-long
        _settings['minute'] = runsql("select value from settings where key='minute'")[0][0]

    # read in username and password
    _settings['username'] = runsql("select value from settings where key='aussiebb_username'")[0][0]
    _settings['password'] = runsql("select value from settings where key='aussiebb_password'")[0][0]
    return _settings


def runtests():
    """Run the dpu port status and speed tests"""

    _settings = getsettings()
    abbportal = portal.AussiePortal(
            _settings['username'],
            _settings['password'],
            debug=False)

    customer = abbportal.customer()

    services = []
    for service_type in customer['services']:
        for service in customer['services'][service_type]:
            service_id = service['service_id']
            services.append((service_type, service_id))

    dpu = abbportal.dpuportstatus(service_id)
    print(dpu)

    # run the speed test
    os.system('docker run --rm -e TZ=Australia/Sydney abb-speedtest')

def saveresults():
    """
    Get the results from AussieBB and save the locally.
    Aussie doesn't keep all of them, so it's better we do.
    """

    _settings = getsettings()
    abbportal = portal.AussiePortal(
            _settings['username'],
            _settings['password'],
            debug=False)

    customer = abbportal.customer()

    services = []
    for service_type in customer['services']:
        for service in customer['services'][service_type]:
            service_id = service['service_id']
            services.append((service_type, service_id))

    # get and populate all the line sync / dpu port status test results
    tests = abbportal.tests(service_id)
    results = runsql('select id from dpuportstatusresults')
    ids = []
    for i in results:
        ids.append(i[0])

    for result in tests:
        if (result['type']) == 'DPU Port Status':
            if result['id'] not in ids:
                output = abbportal.testresult(service_id, result['id'])
                linerate = output['output']['accessLineRate']
                if linerate in ('N/A', "Not Found", None):
                    lineup = 0
                    linedown = 0
                else:
                    linedown = linerate.split('/')[0].replace('>','')
                    lineup = linerate.split('/')[1].split(' ')[0]
                insertline = ("insert into dpuportstatusresults values ('%s', '%s', '%s', '%s', '%s', %s, %s, '%s')"
                        % (output['id'],
                           output['result'],
                           output['output']['syncState'],
                           output['output']['operationalState'],
                           output['output']['reversePowerState'],
                           lineup,linedown,
                           output['completed_at']))
                print(insertline)
                runsql(insertline)

    # get and populate all the spped test results
    tests = abbportal.speedtestresults(service_id)
    results = runsql('select id from speedtestresults')
    ids = []
    for i in results:
        ids.append(i[0])

    for result in tests:
        if result['id'] not in ids:
            insertline = ("insert into speedtestresults values ('%s', '%s', '%s', '%s', '%s', '%s')"
                    % (result['id'],
                       result['server'],
                       result['latencyMs'],
                       result['downloadSpeedKbps'],
                       result['uploadSpeedKbps'],
                       result['date']))
            print(insertline)
            runsql(insertline)

while True:
    time.sleep(60)
    settings = getsettings()
    # is it the minute?
    if datetime.datetime.now().minute != settings['minute']:
        continue
    # is it the hour?
    if datetime.datetime.now().hour%settings['cadence'] != 0:
        continue
    runtests()
    saveresults()
