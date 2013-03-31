#!/usr/bin/env python
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback
import redis,json,time

cq = adapter.couch_queue()
#webdb = redis.Redis(cq.local_config['redis'],db=1)


def callback(ch, method, properties, body):
	try:
		ref = json.loads(body)
		key = method.routing_key
		print ref
		if key == 'id':
			doc = ch.cq.id(ref[1])
			print doc
		ch.basic_ack(delivery_tag = method.delivery_tag)
	except:
		print body
		ch.basic_ack(delivery_tag = method.delivery_tag)
	
if __name__ == "__main__":
	cq = adapter.couch_queue()
	cq.run_queue('out',callback)
