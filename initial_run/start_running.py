import requests
from time import sleep
sleep(30)
if 1==1:
    r=requests.get('http://mage-orc:6789/api/pipelines?include_schedules=1')
    j=r.json()
    for el in j['pipelines']:
        print(el['name'])
        for sh in el['schedules']:
            if sh['name']=='GLOBAL_DATA_PRODUCT_TRIGGER' and sh['schedule_type']=='api':
                trigger_id=sh['id']
    r=requests.post(f'http://mage-orc:6789/api/pipeline_schedules/{trigger_id}/pipeline_runs/fe9b2f2228444b739bf9e191304675d7')
print(r.json())
sleep(100)
if 1==1:
    r=requests.get('http://mage-orc:6789/api/pipelines?include_schedules=1')
    j=r.json()
    for el in j['pipelines']:
        print(el['name'])
        for sh in el['schedules']:
            if sh['name']=='trigger_training' and sh['schedule_type']=='api':
                trigger_id=sh['id']
    r=requests.post(f'http://mage-orc:6789/api/pipeline_schedules/{trigger_id}/pipeline_runs/73dd5fc8d6c84d9aa9d714fa408b2850')
print(r.json())


