#!/usr/bin/env python
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback

def callback(ch, method, properties, body):
	#print body 
	ref = json.loads(body)
	if '_id' in ref:
		cid = ref['_id']
		D =  ch.cq.id(cid)
		ch.basic_ack(delivery_tag = method.delivery_tag)
		#if 'robot_status' in D:
		#	if D['robot_status'] == 'done':
		#		return
		##	print D['robot_status']
		#else:
		#	ch.basic_publish('incoming','new',json.dumps({'_id':cid}))
		#	return
		if 'fail' in D:
			print 'fail '+str(D)
			return
		if 'type' in D:
			#print D['type']
			ch.basic_publish('type_router',D['type'],json.dumps({'_id':cid}))


if __name__ == "__main__":
	cq = adapter.couch_queue()
	cq.run_queue('incoming',callback)
