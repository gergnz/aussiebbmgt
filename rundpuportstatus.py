#!/usr/bin/env python


import os
import aussiebb.portal as portal

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
