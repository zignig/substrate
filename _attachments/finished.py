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
	try:
		ch.cq.write(cid,D)
	except:
		print 'fail'
	ch.basic_ack(delivery_tag = method.delivery_tag)

if __name__ == "__main__": 
	cq = adapter.couch_queue()
	cq.run_queue('finished',callback)
