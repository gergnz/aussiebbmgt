#!/usr/bin/env python3


import os
import aussiebb.portal as portal
from prettytable import PrettyTable
import sqlite3
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

