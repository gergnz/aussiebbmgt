#!/usr/bin/env python3
"""
This will run forever and check the time to see if it should run again.
When it runs it runs a speed test and dpu port status test.
We then fetch the results and save them locally.
"""

import time
import datetime
import os
import json
import random
import sqlite3
import subprocess
import logging
import signal
import psutil
import aussiebb.portal as portal

logging.basicConfig(level=logging.INFO)

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


def runtests(): #pylint: disable=too-many-locals
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
    status = dpu['status']
    testid = dpu['id']
    while status == "InProgress":
        time.sleep(30)
        testresult = abbportal.testresult(service_id, testid)
        status = testresult['status']
        logging.info(testresult)

    # run the speed test
    try:
        p_speedtest = subprocess.run(
                ['/usr/bin/abb-speedtest', '-j'],
                capture_output=True,
                check=True,
                timeout=600
        )
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

    for line in p_speedtest.stdout.decode("utf-8").split('\n'):
        try:
            result = json.loads(line)
            break
        except json.JSONDecodeError:
            pass

    speedid = int(runsql("select id from speedtestresults order by id desc limit 1")[0][0]) + 1

    insertline = ("insert into speedtestresults values ('%s', '%s', '%s', '%s', '%s', '%s')"
            % (speedid,
               result['location'],
               result['ping'],
               int(round(float(result['download'])*1024,0)),
               int(round(float(result['upload'])*1024,0)),
               result['isodate']))
    logging.info(insertline)
    runsql(insertline)

# pylint: disable=too-many-locals, too-many-branches
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
            completed_at = result['date']

            # if we have a Z at the end remove it.
            if completed_at[-1] == 'Z':
                completed_at = completed_at[:-1]

            # This little chunk of code tries to dedup
            time_completed = datetime.datetime.fromisoformat(completed_at)

            # pylint: disable=line-too-long
            query = ("select id from speedtestresults where date > '%s' and date < '%s'"
            % ( str((time_completed - datetime.timedelta(minutes=1)).strftime('%Y-%m-%dT%H:%M:%SZ')),
                str((time_completed - datetime.timedelta(minutes=-1)).strftime('%Y-%m-%dT%H:%M:%SZ'))))
            # pylint: enable=line-too-long

            for result_to_delete in runsql(query):
                delquery = ("delete from speedtestresults where id=%s" % result_to_delete[0])
                logging.info(delquery)
                runsql(delquery)

            # now do the insert of the saved data to use the real id
            insertline = ("insert into speedtestresults values ('%s', '%s', '%s', '%s', '%s', '%s')"
                    % (result['id'],
                       result['server'],
                       result['latencyMs'],
                       result['downloadSpeedKbps'],
                       result['uploadSpeedKbps'],
                       result['date']))
            logging.info(insertline)
            runsql(insertline)
# pylint: enable=too-many-locals, too-many-branches

def timer_expired(signum, frame): #pylint: disable=unused-argument
    """Do something when we the timer expires."""
    logging.error("execution timer expired.")
    raise Exception("we ran out of time")

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
    signal.signal(signal.SIGALRM, timer_expired)
    signal.alarm(300)
    try:
        runtests()
        saveresults()
    except Exception as error: #pylint: disable=broad-except
        logging.error(error)
    signal.alarm(0)
