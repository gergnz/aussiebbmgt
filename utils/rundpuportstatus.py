#!/usr/bin/env python


import os
import time
import logging
import aussiebb.portal as portal

try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client
http_client.HTTPConnection.debuglevel = 1

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

p = portal.AussiePortal(os.environ.get('AUSSIE_USERNAME'),
                        os.environ.get('AUSSIE_PASSWORD'),
                        debug=True)
c = p.customer()

services = []
for service_type in c['services']:
    for service in c['services'][service_type]:
        service_id = service['service_id']
        services.append((service_type, service_id))

dpu = p.dpuportstatus(service_id)
print(dpu)
status = dpu['status']
testid = dpu['id']
while status == "InProgress":
    time.sleep(30)
    testresult = p.testresult(service_id, testid)
    status = testresult['status']
    print(testresult)
