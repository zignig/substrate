#!/usr/bin/env python
import os,subprocess,datetime
import pika,couchdbkit,json
import yaml,adapter,traceback

def now():
    return  datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%Sz')

def callback(ch, method, properties, body):
	server = ch.couch
	database = ch.cq.db 
	ref = json.loads(body)
	cid = ref['_id']
	D = ch.cq.cur_id(cid)
	D['robot_status'] = 'running'
	print 'pending: '+cid
	ch.cq.save(cid,D)
	ch.basic_ack(delivery_tag = method.delivery_tag)

cq = adapter.couch_queue()
cq.run_queue('pending',callback)
