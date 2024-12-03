import json
import os
import signal
import uuid

import requests

from dg_spider.libs.models import Task
from dg_spider.libs.mysql_client import MysqlClient


args = {
  "spider": {
	"website_id": 2268,
	"started_by_scrapy": True,
	"save_to_mysql": True
  },
  "timer": {
	"enabled": False,
	"crawl_until_datetime": ""
  },
  "audit": {
	"enabled": True,
	"audit_id": 1
  },
  "proxy": {
	"enabled": False,
	"mode": "lab",
	"temp": {
	  "ip": "",
	  "port": 1234
	}
  }
}




with MysqlClient.get_session() as session, session.begin():
    task_id = str(uuid.uuid4())
    session.add(Task(id=task_id, argument=args))
    url = f'http://localhost:6800/schedule.json'
    data = {'project': 'dg_spider', 'spider': 'mzamin', 'jobid': task_id, 'task_id': task_id}
    requests.post(url, data=data)

# url = f'http://localhost:6800/listjobs.json'
# running_jobs = requests.get(url).json()['running']
# for job in running_jobs:
#     if job['id'] == "a235d54c-426b-429d-8f8e-6a0a116aa56a":
#         print(job['pid'])
#         os.kill(job['pid'], signal.SIGKILL)
