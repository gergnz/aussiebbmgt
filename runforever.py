#!/usr/bin/env python
"""
This will run forever and check the time to see if it should run again.
When it runs it runs a speed test and dpu port status test.
We then fetch the results and save them locally.
"""

import time
import datetime
import os
import sqlite3
import aussiebb.portal as portal

# read in the random minute and/or set it
# read in the cadence

minute = 52
cadence = 1 # Wondering if we should check this regularly... a function maybe?


# read in username and password


def runtests():
    """Run the dpu port status and speed tests"""
    # run the dpu port status / line sync test
    p = portal.AussiePortal(os.environ.get('AUSSIE_USERNAME'),
                            os.environ.get('AUSSIE_PASSWORD'),
                            debug=False)
    c = p.customer()

    services = []
    for service_type in c['services']:
        for service in c['services'][service_type]:
            service_id = service['service_id']
            services.append((service_type, service_id))

    dpu = p.dpuportstatus(service_id)
    print(dpu)

    # run the speed test
    os.system('docker run --rm -e TZ=Australia/Sydney abb-speedtest')

def saveresults():
    """
    Get the results from AussieBB and save the locally.
    Aussie doesn't keep all of them, so it's better we do.
    """
    conn = sqlite3.connect('aussiebbmgt.db')

    p = portal.AussiePortal(os.environ.get('AUSSIE_USERNAME'),
                            os.environ.get('AUSSIE_PASSWORD'),
                            debug=False)
    c = p.customer()

    services = []
    for service_type in c['services']:
        for service in c['services'][service_type]:
            service_id = service['service_id']
            services.append((service_type, service_id))

    cursor = conn.cursor()

    # get and populate all the line sync / dpu port status test results
    tests = p.tests(service_id)
    results = cursor.execute('select id from dpuportstatusresults')
    ids = []
    for i in results.fetchall():
        ids.append(i[0])

    for result in tests:
        if (result['type']) == 'DPU Port Status':
            if result['id'] not in ids:
                output = p.testresult(service_id, result['id'])
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
                cursor.execute(insertline)
                conn.commit()

    # get and populate all the spped test results
    tests = p.speedtestresults(service_id)
    results = cursor.execute('select id from speedtestresults')
    ids = []
    for i in results.fetchall():
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
            cursor.execute(insertline)
            conn.commit()

    conn.close()


while True:
    time.sleep(60)
    # is it the minute?
    if datetime.datetime.now().minute != minute:
        continue
    # is it the hour?
    if datetime.datetime.now().hour%cadence != 0:
        continue
    runtests()
    saveresults()
