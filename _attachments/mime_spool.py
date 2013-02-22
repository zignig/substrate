#!/usr/bin/env python
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback
import redis,json,time,StringIO

def callback(ch, method, properties, body):
	try:
		ref = json.loads(body)
		key = method.routing_key
		print key,ref
		#do stuff
		ch.basic_ack(delivery_tag = method.delivery_tag)
	except:
		print body
		ch.basic_ack(delivery_tag = method.delivery_tag)
	
def get_all(mime_type='image/jpeg'):
	a = cq.db.view('robot/mime_types',reduce=False,key=mime_type).all()
	for i in a:
	 	#print i	
		cq.channel.basic_publish('mime_types','mime_type:'+mime_type,json.dumps(i))	

def get_types():
	types = cq.db.view('robot/mime_types',group=True).all()
	for i in types:
		print i['key']
		get_all(i['key'])
	
	
if __name__ == "__main__":
	cq = adapter.couch_queue()
	get_types()
	#cq.run_queue('mime_type:image/jpeg',callback)

