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
	cid = ref['id']
	print "reset :"+cid
	D = ch.cq.id(cid) 
	#D['complete'] = False
	#D['type'] = 'thing'
#	if D.has_key('keywords'):
#		D['tags'] = D['keywords']
	if D.has_key('robot_status'):
		del D['robot_status'] 
	try:
		ch.cq.save(cid,D)
	except:
		print 'fail save'
	ch.basic_ack(delivery_tag = method.delivery_tag)

cq = adapter.couch_queue()
cq.run_queue('out',callback)
