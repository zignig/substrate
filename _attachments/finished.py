#!/usr/bin/env python
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback

def callback(ch, method, properties, body):
	ref = json.loads(body)
	cid = ref['_id']
	D =  ch.cq.id(cid)
	print('finished :'+cid)
	D['robot_status'] = 'done'
	ch.cq.write(cid,D)
	ch.basic_ack(delivery_tag = method.delivery_tag)

cq = adapter.couch_queue()
cq.run_queue('finished',callback)
