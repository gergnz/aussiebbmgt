#!/usr/bin/env python3
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
import subprocess
import logging
import psutil
import aussiebb.portal as portal

_DEBUG=False
if os.environ.get('FLASK_ENV') == 'development':
    logging.basicConfig(level='DEBUG')
    _DEBUG=True

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
            debug=_DEBUG)

    customer = abbportal.customer()

    services = []
    for service_type in customer['services']:
        for service in customer['services'][service_type]:
            service_id = service['service_id']
            services.append((service_type, service_id))

    dpu = abbportal.dpuportstatus(service_id)
    logging.info(dpu)

    # run the speed test
    try:
        proc = subprocess.run(['/usr/bin/abb-speedtest'], check=True, timeout=600)
    except subprocess.TimeoutExpired:
        logging.error('speed test timedout')
        for proc in psutil.process_iter():
            if proc.name() == 'chrome':
                proc.kill()
    except subprocess.CalledProcessError:
        logging.error('speed test failed')
        for proc in psutil.process_iter():
            if proc.name() == 'chrome':
                proc.kill()
    os.system('/bin/rm -rf /tmp/lighthouse.X*')

# pylint: disable=too-many-locals
def saveresults():
    """
    Get the results from AussieBB and save the locally.
    Aussie doesn't keep all of them, so it's better we do.
    """

    _settings = getsettings()
    abbportal = portal.AussiePortal(
            _settings['username'],
            _settings['password'],
            debug=_DEBUG)

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
                # pylint: disable=line-too-long
                insertline = ("insert into dpuportstatusresults values ('%s', '%s', '%s', '%s', '%s', %s, %s, '%s', '%s')"
                # pylint: enable=line-too-long
                        % (output['id'],
                           output['result'],
                           output['output']['syncState'],
                           output['output']['operationalState'],
                           output['output']['reversePowerState'],
                           lineup,linedown,
                           output['completed_at'],
                           output['status']))
                logging.info(insertline)
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
            logging.info(insertline)
            runsql(insertline)
# pylint: enable=too-many-locals

logging.info("starting runforever")
while True:
    time.sleep(60)
    settings = getsettings()
    logging.debug(settings)
    logging.debug(datetime.datetime.now())
    # is it the minute?
    if datetime.datetime.now().minute != int(settings['minute']):
        logging.debug("wrong minute")
        continue
    # is it the hour?
    if datetime.datetime.now().hour%int(settings['cadence']) != 0:
        logging.debug("wrong hour")
        continue
    logging.debug("it's the right time, let's run the tests and get the results")
    runtests()
    saveresults()
