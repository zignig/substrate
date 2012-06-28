#!/usr/bin/env python
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback

def callback(ch, method, properties, body):
	print body
	ref = json.loads(body)
	cid = ref['_id']
	D =  ch.cq.id(cid)
	print(D['type'])
	ch.basic_ack(delivery_tag = method.delivery_tag)

cq = adapter.couch_queue()
cq.run_queue('incoming',callback)
