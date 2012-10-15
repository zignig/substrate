#!/usr/bin/env python
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback

def callback(ch, method, properties, body):
	ref = json.loads(body)
	print ref
	print cq.redis.hgetall('bobbin')
	for i in ref['services']:
		val = cq.redis.hget('bobbin',i)
		if val <> None:
			if int(val)  > 0:
				print 'start '+i+' on '+ref['queue']
				cq.redis.hincrby('bobbin',i,1)
				cq.channel.basic_publish('',ref['queue'],i)

	ch.basic_ack(delivery_tag = method.delivery_tag)
	
if __name__ == "__main__":
	cq = adapter.couch_queue()
	cq.redis.hincrby('bobbin','download',2)
	cq.redis.hincrby('bobbin','incoming',2)
	cq.redis.hincrby('bobbin','thingiverse',2)
	cq.redis.hincrby('bobbin','stl',2)
	cq.run_queue('notify',callback)
