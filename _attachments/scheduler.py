#!/usr/bin/env python
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback
import redis,json,time
from apscheduler.scheduler import Scheduler

def echo(val='empty'):
	print val 

def callback(ch, method, properties, body):
	try:
		ref = json.loads(body)
		key = method.routing_key
		print ref
		if 'seconds' in ref.keys():
			if 'command' in ref.keys():
				ch.cq.sched.add_interval_job(echo,seconds=ref['seconds'],args=[ref['command']])
			else:
				ch.cq.sched.add_interval_job(echo,seconds=ref['seconds'])
			
		ch.basic_ack(delivery_tag = method.delivery_tag)
	except:
		print 'FAIL'
		print body
		ch.basic_ack(delivery_tag = method.delivery_tag)
	
if __name__ == "__main__":
	cq = adapter.couch_queue()
	cq.sched = Scheduler()
	cq.channel.basic_publish('command','notify',json.dumps({'scheduler':'empty'}))
	cq.sched.start()
	cq.run_queue('schedule',callback)
