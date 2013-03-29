#!/usr/bin/env python
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback

def callback(ch, method, properties, body):
	ref = json.loads(body)
	print 'later '+body
	#ch.basic_publish('error','error',json.dumps({'fix_later':ref}))
	ch.basic_ack(delivery_tag = method.delivery_tag)

if __name__ == "__main__": 
	cq = adapter.couch_queue()
	cq.run_queue('later',callback)
