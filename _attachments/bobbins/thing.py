#!/usr/bin/env python
import os,subprocess,datetime
import pika,couchdbkit,json
import yaml,adapter,traceback

def now():
    return  datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%Sz')

def callback(ch, method, properties, body):
	ref = json.loads(body)
	cid = ref['_id']
	D = ch.cq.cur_id(cid)
	print D
	ch.basic_ack(delivery_tag = method.delivery_tag)

if __name__ == "__main__":
	cq = adapter.couch_queue()
	cq.run_queue('thing',callback)
