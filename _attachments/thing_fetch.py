#!/usr/bin/env python
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback

def callback(ch, method, properties, body):
	#print body
	try:
		ref = json.loads(body)
		cid = ref['_id']
		#print("template : "+str(cid))
		D = ch.cq.id(cid) 
		print D['name']
		for i in D['thingi_download']:
			mess = {}
			mess['_id'] = cid
			mess['host'] = 'thingiverse.com'
			mess['url'] = 'http://thingiverse.com'+i[0]
			mess['path'] = i[0]
			mess['name'] = i[1]
			ch.basic_publish('','download',json.dumps(mess))
	except :
		print 'error'
		print body
		ch.basic_publish('','error',str(traceback.print_exc()))
	ch.basic_ack(delivery_tag = method.delivery_tag)
	
if __name__ == "__main__":
	cq = adapter.couch_queue()
	cq.run_queue('thingiverse',callback)
