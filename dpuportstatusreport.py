#!/usr/bin/env python3


import os
import aussiebb.portal as portal
from prettytable import PrettyTable
import sqlite3
conn = sqlite3.connect('dpuportstatus.db')


p = portal.AussiePortal(os.environ.get('AUSSIE_USERNAME'),
                        os.environ.get('AUSSIE_PASSWORD'),
                        debug=False)
c = p.customer()

services = []
for service_type in c['services']:
    for service in c['services'][service_type]:
        service_id = service['service_id']
        services.append((service_type, service_id))

c = conn.cursor()
tests = p.tests(service_id)
results = c.execute('select id from dpuportstatusresults')
ids = []
for i in results.fetchall():
    ids.append(i[0])

for result in tests:
    if (result['type']) == 'DPU Port Status':
        if result['id'] not in ids:
            output = p.testresult(service_id, result['id'])
            linerate = output['output']['accessLineRate']
            if linerate == 'N/A' or linerate == "Not Found" or linerate == None:
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
            c.execute(insertline)
            conn.commit()
conn.close()

