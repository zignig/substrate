#!/usr/bin/env python
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback

def callback(ch, method, properties, body):
	ref = json.loads(body)
	cq.basic_publish('error','error',json.dumps({'info':body,'openscad':'process'}))
	ch.basic_ack(delivery_tag = method.delivery_tag)

if __name__ == "__main__": 
	cq = adapter.couch_queue()
	cq.run_queue('openscad',callback)
