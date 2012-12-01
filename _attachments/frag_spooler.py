#!/usr/bin/env python
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback
import redis,json,time

cq = adapter.couch_queue()
webdb = redis.Redis(cq.local_config['redis'],db=1)


def callback(ch, method, properties, body):
	try:
		ref = json.loads(body)
		key = method.routing_key
		print ref
		if key == 'id':
			doc = ch.cq.id(ref[1])
			webdb.set('id:'+ref[1],json.dumps(doc['name']))
		else:
			ret = ch.cq.queries[key](ref[1][1])
			print ret
			d = json.dumps([ref[1],ret])
			webdb.set(ref[0],d)
			webdb.expire(ref[0],10)
		#cid = ref['key']
		#print("template : "+str(cid))
		#D = ch.cq.id(cid) 
		ch.basic_ack(delivery_tag = method.delivery_tag)
	
	except:
		print body
		ch.basic_ack(delivery_tag = method.delivery_tag)
	
if __name__ == "__main__":
	cq = adapter.couch_queue()
	cq.run_queue('frag_known',callback)
